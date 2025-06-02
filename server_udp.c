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

    struct timeval tv;
    tv.tv_sec = 1;
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
        close(sockfd);
        return -1;
    }

    socklen_t addr_len = sizeof(servaddr);
    if (getsockname(sockfd, (struct sockaddr *)&servaddr, &addr_len) == 0)
    {
        printf("[SERVER] UDP servidor iniciado e ouvindo em %s:%d\n",
               inet_ntoa(servaddr.sin_addr), ntohs(servaddr.sin_port));
    }

    printf("[DEBUG] Para testar conectividade externa:\n");
    printf("[DEBUG]   1. No WSL: netstat -ulnp | grep %d\n", port);
    printf("[DEBUG]   2. No Windows: netstat -an | findstr %d\n", port);
    printf("[DEBUG]   3. Do cliente: nc -u <ip_wsl> %d\n", port);

    return sockfd;
}

static int handle_one_packet(int sockfd, unsigned char *buffer)
{
    struct sockaddr_in cliaddr;
    socklen_t len = sizeof(cliaddr);

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
            return 0;
        }
        if (running)
        {
            perror("recvfrom");
        }
        return -1;
    }

    printf("[SERVER] ✓ Recebido %zd bytes de %s:%d — ecoando de volta\n",
           nbytes,
           inet_ntoa(cliaddr.sin_addr),
           ntohs(cliaddr.sin_port));

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
        return -1;
    }
    else
    {
        printf("DEBUG_SERVER: enviou %zd bytes para %s:%d\n", sent,
               inet_ntoa(cliaddr.sin_addr), ntohs(cliaddr.sin_port));
    }
    if (sent != nbytes)
    {
        printf("[WARN] Enviado apenas %zd de %zd bytes\n", sent, nbytes);
    }

    return 0;
}

static void serve_forever(int sockfd)
{
    unsigned char buffer[MAX_BUFFER];
    printf("[SERVER] Aguardando conexões... (Ctrl+C para parar)\n");

    while (running)
    {
        handle_one_packet(sockfd, buffer);
    }

    printf("[SERVER] Servidor parado.\n");
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
