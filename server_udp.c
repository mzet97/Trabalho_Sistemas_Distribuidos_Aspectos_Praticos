#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <signal.h>

#define MAX_BUFFER 65536

static volatile int running = 1;
static int server_sockfd = -1;

static void signal_handler(int sig)
{
    printf("\n[SERVER] Recebido sinal %d, parando servidor...\n", sig);
    running = 0;
    if (server_sockfd >= 0)
    {
        close(server_sockfd);
        server_sockfd = -1;
    }
}

static int setup_socket(const char *listen_ip, int port)
{
    int sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0)
    {
        perror("socket");
        return -1;
    }

    int opt = 1;
    if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0)
    {
        perror("setsockopt SO_REUSEADDR");
        close(sockfd);
        return -1;
    }

    if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEPORT, &opt, sizeof(opt)) < 0)
    {
        perror("setsockopt SO_REUSEPORT (ignorando erro)");
    }

    // Aumentar buffer de recepção
    int rcvbuf = 262144; // 256KB
    if (setsockopt(sockfd, SOL_SOCKET, SO_RCVBUF, &rcvbuf, sizeof(rcvbuf)) < 0)
    {
        perror("setsockopt SO_RCVBUF (ignorando erro)");
    }

    // Remover timeout muito restritivo para debug
    struct timeval tv;
    tv.tv_sec = 5; // Aumentado de 1 para 5 segundos
    tv.tv_usec = 0;
    if (setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv)) < 0)
    {
        perror("setsockopt SO_RCVTIMEO");
        close(sockfd);
        return -1;
    }

    struct sockaddr_in servaddr;
    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(port);

    if (strcmp(listen_ip, "0.0.0.0") == 0 || strlen(listen_ip) == 0)
    {
        servaddr.sin_addr.s_addr = INADDR_ANY;
        printf("[SERVER] Configurado para escutar em todas as interfaces (0.0.0.0:%d)\n", port);
    }
    else
    {
        if (inet_aton(listen_ip, &servaddr.sin_addr) == 0)
        {
            fprintf(stderr, "IP inválido para bind: %s\n", listen_ip);
            close(sockfd);
            return -1;
        }
        printf("[SERVER] Configurado para escutar no IP específico %s:%d\n", listen_ip, port);
    }

    if (bind(sockfd, (struct sockaddr *)&servaddr, sizeof(servaddr)) < 0)
    {
        perror("bind");
        printf("[DEBUG] Falha ao fazer bind no endereço %s:%d\n",
               (servaddr.sin_addr.s_addr == INADDR_ANY) ? "0.0.0.0" : listen_ip, port);
        printf("[DEBUG] Verifique se a porta não está em uso: netstat -ulnp | grep %d\n", port);
        printf("[DEBUG] Erro específico: %s\n", strerror(errno));
        close(sockfd);
        return -1;
    }

    socklen_t addr_len = sizeof(servaddr);
    if (getsockname(sockfd, (struct sockaddr *)&servaddr, &addr_len) == 0)
    {
        printf("[SERVER] ✓ UDP servidor ATIVO em %s:%d\n",
               inet_ntoa(servaddr.sin_addr), ntohs(servaddr.sin_port));
    }

    printf("[DEBUG] Para testar conectividade:\n");
    printf("[DEBUG]   1. WSL: ss -ulnp | grep %d\n", port);
    printf("[DEBUG]   2. Windows: netsh interface portproxy show all\n");
    printf("[DEBUG]   3. Teste: echo 'TEST' | nc -u <ip_wsl> %d\n", port);
    printf("[DEBUG] Aguardando primeiro pacote...\n");

    return sockfd;
}

static int handle_one_packet(int sockfd, unsigned char *buffer)
{
    struct sockaddr_in cliaddr;
    socklen_t len = sizeof(cliaddr);

    printf("[SERVER] Aguardando recepção de dados...\n");

    ssize_t nbytes = recvfrom(
        sockfd,
        buffer,
        MAX_BUFFER,
        0,
        (struct sockaddr *)&cliaddr,
        &len);

    if (nbytes < 0)
    {
        if (errno == EWOULDBLOCK || errno == EAGAIN)
        {
            printf("[SERVER] Timeout na recepção (nenhum dado recebido)\n");
            return 0;
        }
        if (running)
        {
            perror("recvfrom");
            printf("[ERROR] Erro na recepção: %s\n", strerror(errno));
        }
        return -1;
    }

    printf("[SERVER] ✓ RECEBIDO %zd bytes de %s:%d\n",
           nbytes,
           inet_ntoa(cliaddr.sin_addr),
           ntohs(cliaddr.sin_port));

    // Log dos primeiros bytes para debug
    printf("[DEBUG] Primeiros bytes: ");
    for (int i = 0; i < (nbytes > 16 ? 16 : nbytes); i++)
    {
        printf("%02x ", buffer[i]);
    }
    printf("\n");

    printf("[SERVER] Ecoando %zd bytes de volta...\n", nbytes);

    ssize_t sent = sendto(
        sockfd,
        buffer,
        nbytes,
        0,
        (struct sockaddr *)&cliaddr,
        len);

    if (sent < 0)
    {
        perror("sendto");
        printf("[ERROR] Falha ao enviar resposta: %s\n", strerror(errno));
        return -1;
    }

    printf("[SERVER] ✓ ENVIADO %zd bytes de volta para %s:%d\n",
           sent, inet_ntoa(cliaddr.sin_addr), ntohs(cliaddr.sin_port));

    if (sent != nbytes)
    {
        printf("[WARN] Enviado apenas %zd de %zd bytes\n", sent, nbytes);
    }

    return 1; // Sucesso
}

static void serve_forever(int sockfd)
{
    unsigned char buffer[MAX_BUFFER];
    int packet_count = 0;

    printf("[SERVER] 🚀 Servidor ATIVO - aguardando conexões...\n");
    printf("[SERVER] (Ctrl+C para parar)\n");

    while (running)
    {
        int result = handle_one_packet(sockfd, buffer);
        if (result > 0)
        {
            packet_count++;
            printf("[SERVER] Total de pacotes processados: %d\n", packet_count);
        }
        else if (result < 0)
        {
            printf("[ERROR] Erro no processamento do pacote\n");
        }
    }

    printf("[SERVER] Servidor parado após processar %d pacotes.\n", packet_count);
}

int main(int argc, char *argv[])
{
    if (argc != 3)
    {
        fprintf(stderr, "Uso: %s <listen_ip> <port>\n", argv[0]);
        fprintf(stderr, "  <listen_ip>: IP para bind (use '0.0.0.0' para todas as interfaces)\n");
        fprintf(stderr, "  <port>: Porta UDP para escutar\n");
        fprintf(stderr, "\nExemplos:\n");
        fprintf(stderr, "  %s 0.0.0.0 50000        # Escuta em todas as interfaces\n", argv[0]);
        fprintf(stderr, "  %s 10.0.0.12 50000      # Escuta apenas no IP específico\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *listen_ip = argv[1];
    int port = atoi(argv[2]);

    if (port <= 0 || port > 65535)
    {
        fprintf(stderr, "Porta inválida: %d (deve estar entre 1-65535)\n", port);
        return EXIT_FAILURE;
    }

    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);

    printf("[SERVER] Iniciando servidor UDP...\n");
    printf("[DEBUG] IP: %s, Porta: %d\n", listen_ip, port);

    server_sockfd = setup_socket(listen_ip, port);
    if (server_sockfd < 0)
    {
        return EXIT_FAILURE;
    }

    serve_forever(server_sockfd);

    if (server_sockfd >= 0)
    {
        close(server_sockfd);
    }
    return EXIT_SUCCESS;
}
