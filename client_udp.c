#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <time.h>
#include <arpa/inet.h>
#include <sys/stat.h>
#include <sys/socket.h>

#define NUM_MEASURES 1000
#define WARMUP 50
#define MAX_BUFFER 65536
#define MAX_UDP_PAYLOAD 65507

static const int sizes[] = {
    2, 4, 8, 16, 32, 64, 128, 256,
    512, 1024, 2048, 4096, 8192, 16384, 32768, MAX_UDP_PAYLOAD};
static const int NSIZES = sizeof(sizes) / sizeof(sizes[0]);

static double diff_ms(const struct timespec *start, const struct timespec *end)
{
    time_t sec_diff = end->tv_sec - start->tv_sec;
    long nsec_diff = end->tv_nsec - start->tv_nsec;
    return (double)sec_diff * 1e3 + (double)nsec_diff / 1e6;
}

static int file_exists(const char *path)
{
    struct stat buf;
    return (stat(path, &buf) == 0);
}

static FILE *open_csv(const char *filename)
{
    int exists = file_exists(filename);
    FILE *fp = fopen(filename, "a");
    if (!fp)
    {
        perror("fopen");
        return NULL;
    }
    if (!exists)
    {
        fprintf(fp, "tamanho_bytes,iteracao,rtt_ms\n");
    }
    return fp;
}

static int setup_socket(const char *local_ip)
{
    int sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0)
    {
        perror("socket");
        return -1;
    }

    // Aumentar buffers
    int sndbuf = 262144, rcvbuf = 262144;
    setsockopt(sockfd, SOL_SOCKET, SO_SNDBUF, &sndbuf, sizeof(sndbuf));
    setsockopt(sockfd, SOL_SOCKET, SO_RCVBUF, &rcvbuf, sizeof(rcvbuf));

    if (strcmp(local_ip, "auto") == 0 || strcmp(local_ip, "0.0.0.0") == 0)
    {
        printf("[CLIENT] ✓ Usando bind automático (sistema escolhe interface)\n");
    }
    else
    {
        struct sockaddr_in localaddr;
        memset(&localaddr, 0, sizeof(localaddr));
        localaddr.sin_family = AF_INET;
        localaddr.sin_port = htons(0);

        if (inet_aton(local_ip, &localaddr.sin_addr) == 0)
        {
            fprintf(stderr, "IP local inválido: %s\n", local_ip);
            close(sockfd);
            return -1;
        }

        if (bind(sockfd, (struct sockaddr *)&localaddr, sizeof(localaddr)) < 0)
        {
            perror("bind local");
            printf("[WARN] Falha no bind em %s - usando bind automático\n", local_ip);
        }
        else
        {
            printf("[CLIENT] ✓ Bind local feito em %s\n", local_ip);
        }
    }

    struct timeval tv;
    tv.tv_sec = 10; // Aumentado para 10 segundos
    tv.tv_usec = 0;
    if (setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv)) < 0)
    {
        perror("setsockopt");
        close(sockfd);
        return -1;
    }

    struct sockaddr_in local_info;
    socklen_t local_len = sizeof(local_info);
    if (getsockname(sockfd, (struct sockaddr *)&local_info, &local_len) == 0)
    {
        printf("[CLIENT] 🔗 Socket local: %s:%d\n",
               inet_ntoa(local_info.sin_addr), ntohs(local_info.sin_port));
    }

    return sockfd;
}

static void do_warmup(int sockfd, struct sockaddr_in *servaddr, int payload_size, unsigned char *buffer)
{
    for (int w = 0; w < WARMUP; w++)
    {
        ssize_t sent = sendto(sockfd, buffer, payload_size, 0,
                              (struct sockaddr *)servaddr, sizeof(*servaddr));
        if (sent < 0)
        {
            perror("sendto (warmup)");
        }
        else
        {
            printf("[DEBUG_CLIENT] Enviado %zd bytes para %s:%d\n",
                   sent, inet_ntoa(servaddr->sin_addr), ntohs(servaddr->sin_port));
        }
        (void)recvfrom(sockfd, buffer, payload_size, 0, NULL, NULL);
    }
}

static void measure_for_size(int sockfd, struct sockaddr_in *servaddr, int payload_size, FILE *fp)
{
    unsigned char buffer[MAX_BUFFER];
    memset(buffer, 'A', payload_size);

    printf("[TEST] 🧪 Iniciando teste para %d bytes\n", payload_size);

    do_warmup(sockfd, servaddr, payload_size, buffer);

    int success_count = 0;
    int timeout_count = 0;
    int error_count = 0;

    for (int i = 1; i <= NUM_MEASURES; i++)
    {
        struct timespec t_start, t_end;
        double rtt_ms;

        if (clock_gettime(CLOCK_MONOTONIC, &t_start) < 0)
        {
            perror("clock_gettime start");
            continue;
        }

        printf("[CLIENT] 📤 Enviando pacote %d/%d (%d bytes) para %s:%d\n",
               i, NUM_MEASURES, payload_size,
               inet_ntoa(servaddr->sin_addr), ntohs(servaddr->sin_port));

        ssize_t sent = sendto(sockfd, buffer, payload_size, 0,
                              (struct sockaddr *)servaddr, sizeof(*servaddr));
        if (sent < 0)
        {
            perror("sendto");
            printf("[ERROR] ❌ Falha ao enviar pacote %d (erro: %s)\n", i, strerror(errno));
            fprintf(fp, "%d,%d,%.3f\n", payload_size, i, -1.0);
            error_count++;
            continue;
        }
        else if (sent != payload_size)
        {
            printf("[WARN] ⚠️ Enviado apenas %zd de %d bytes\n", sent, payload_size);
        }

        printf("[CLIENT] 📥 Aguardando resposta do servidor...\n");

        ssize_t rec = recvfrom(sockfd, buffer, payload_size, 0, NULL, NULL);
        if (rec < 0)
        {
            if (errno == EWOULDBLOCK || errno == EAGAIN)
            {
                printf("[TIMEOUT] ⏰ Timeout na resposta do pacote %d\n", i);
                timeout_count++;
            }
            else
            {
                perror("recvfrom");
                printf("[ERROR] ❌ Erro no recvfrom do pacote %d: %s\n", i, strerror(errno));
                error_count++;
            }
            fprintf(fp, "%d,%d,%.3f\n", payload_size, i, -1.0);
            continue;
        }

        if (clock_gettime(CLOCK_MONOTONIC, &t_end) < 0)
        {
            perror("clock_gettime end");
            fprintf(fp, "%d,%d,%.3f\n", payload_size, i, -1.0);
            continue;
        }

        if (rec != payload_size)
        {
            printf("[WARN] ⚠️ Recebido %zd bytes (esperavam %d)\n", rec, payload_size);
        }

        rtt_ms = diff_ms(&t_start, &t_end);
        fprintf(fp, "%d,%d,%.5f\n", payload_size, i, rtt_ms);
        printf("[SUCCESS] ✅ RTT = %.3f ms\n", rtt_ms);
        success_count++;
    }

    printf("[STATS] Para %d bytes: %d sucessos, %d timeouts, %d erros\n",
           payload_size, success_count, timeout_count, error_count);
}

static void run_tests(int sockfd, struct sockaddr_in *servaddr, FILE *fp)
{
    for (int idx = 0; idx < NSIZES; idx++)
    {
        int payload_size = sizes[idx];
        printf("[TEST] Medindo payload = %d bytes\n", payload_size);
        measure_for_size(sockfd, servaddr, payload_size, fp);
        usleep(100000);
    }
}

int main(int argc, char *argv[])
{
    if (argc != 5)
    {
        fprintf(stderr,
                "Uso: %s <local_ip> <server_ip> <server_port> <client_id>\n"
                "  <local_ip>   : IP do cliente (ex.: 10.0.0.11) ou 'auto' para automático\n"
                "  <server_ip>  : IP do servidor UDP (ex.: 10.0.0.12)\n"
                "  <server_port>: Porta UDP do servidor (ex.: 50000)\n"
                "  <client_id>  : ID do cliente (1 ou 2)\n",
                argv[0]);
        return EXIT_FAILURE;
    }

    const char *local_ip = argv[1];
    const char *server_ip = argv[2];
    int server_port = atoi(argv[3]);
    int client_id = atoi(argv[4]);
    if (!(client_id == 1 || client_id == 2))
    {
        fprintf(stderr, "client_id deve ser 1 ou 2\n");
        return EXIT_FAILURE;
    }

    printf("[CLIENT %d] 🚀 Iniciando cliente...\n", client_id);
    printf("[DEBUG] Local IP: %s, Server: %s:%d\n", local_ip, server_ip, server_port);

    // Teste de conectividade básica
    printf("[CLIENT] 🔍 Testando conectividade com servidor...\n");

    int sockfd = setup_socket(local_ip);
    if (sockfd < 0)
    {
        return EXIT_FAILURE;
    }

    struct sockaddr_in servaddr;
    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(server_port);
    if (inet_aton(server_ip, &servaddr.sin_addr) == 0)
    {
        fprintf(stderr, "❌ Endereço IP inválido: %s\n", server_ip);
        close(sockfd);
        return EXIT_FAILURE;
    }

    printf("[CLIENT] 🎯 Conectando com servidor %s:%d\n", server_ip, server_port);

    // Teste de conectividade simples
    char test_msg[] = "CONNECTIVITY_TEST";
    ssize_t test_sent = sendto(sockfd, test_msg, strlen(test_msg), 0,
                               (struct sockaddr *)&servaddr, sizeof(servaddr));
    if (test_sent < 0)
    {
        perror("Teste de conectividade falhou");
        printf("[ERROR] ❌ Não foi possível enviar dados para o servidor\n");
        close(sockfd);
        return EXIT_FAILURE;
    }

    char test_response[64];
    ssize_t test_rec = recvfrom(sockfd, test_response, sizeof(test_response), 0, NULL, NULL);
    if (test_rec < 0)
    {
        printf("[ERROR] ❌ Servidor não respondeu ao teste de conectividade\n");
        printf("[DEBUG] Verifique se o servidor está rodando em %s:%d\n", server_ip, server_port);
        close(sockfd);
        return EXIT_FAILURE;
    }

    printf("[CLIENT] ✅ Conectividade OK - servidor respondeu com %zd bytes\n", test_rec);

    char filename[64];
    snprintf(filename, sizeof(filename), "raw_data_cliente%d.csv", client_id);
    FILE *fp = open_csv(filename);
    if (!fp)
    {
        close(sockfd);
        return EXIT_FAILURE;
    }

    run_tests(sockfd, &servaddr, fp);

    printf("[CLIENT %d] Testes concluídos. Dados em: %s\n", client_id, filename);
    fclose(fp);
    close(sockfd);
    return EXIT_SUCCESS;
}
