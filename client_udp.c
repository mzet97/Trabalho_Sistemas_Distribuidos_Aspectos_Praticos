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
        close(sockfd);
        return -1;
    }

    struct timeval tv;
    tv.tv_sec = 2;
    tv.tv_usec = 0;
    if (setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv)) < 0)
    {
        perror("setsockopt");
        close(sockfd);
        return -1;
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
        (void)recvfrom(sockfd, buffer, payload_size, 0, NULL, NULL);
    }
}

static void measure_for_size(int sockfd, struct sockaddr_in *servaddr, int payload_size, FILE *fp)
{
    unsigned char buffer[MAX_BUFFER];
    memset(buffer, 'A', payload_size);

    do_warmup(sockfd, servaddr, payload_size, buffer);

    for (int i = 1; i <= NUM_MEASURES; i++)
    {
        struct timespec t_start, t_end;
        double rtt_ms;

        if (clock_gettime(CLOCK_MONOTONIC, &t_start) < 0)
        {
            perror("clock_gettime start");
            continue;
        }

        ssize_t sent = sendto(sockfd, buffer, payload_size, 0,
                              (struct sockaddr *)servaddr, sizeof(*servaddr));
        if (sent < 0)
        {
            perror("sendto (measure)");
            fprintf(fp, "%d,%d,%.3f\n", payload_size, i, -1.0);
            continue;
        }

        ssize_t rec = recvfrom(sockfd, buffer, payload_size, 0, NULL, NULL);
        if (rec < 0)
        {
            if (errno == EWOULDBLOCK || errno == EAGAIN)
            {
                fprintf(fp, "%d,%d,%.3f\n", payload_size, i, -1.0);
            }
            else
            {
                perror("recvfrom");
                fprintf(fp, "%d,%d,%.3f\n", payload_size, i, -1.0);
            }
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
            fprintf(stderr,
                    "[WARN] recvfrom rec=%zd bytes (esperavam %d)\n",
                    rec, payload_size);
        }

        rtt_ms = diff_ms(&t_start, &t_end);
        fprintf(fp, "%d,%d,%.5f\n", payload_size, i, rtt_ms);
    }
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
                "  <local_ip>   : IP do cliente (ex.: 10.0.10.11)\n"
                "  <server_ip>  : IP do servidor UDP (ex.: 10.0.10.12)\n"
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
        fprintf(stderr, "Endereço IP inválido: %s\n", server_ip);
        close(sockfd);
        return EXIT_FAILURE;
    }

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
