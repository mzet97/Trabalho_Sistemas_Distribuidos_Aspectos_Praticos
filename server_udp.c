#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>

#define MAX_BUFFER 65536

static int setup_socket(const char *listen_ip, int port)
{
    int sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0)
    {
        perror("socket");
        return -1;
    }

    struct sockaddr_in servaddr;
    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(port);
    if (inet_aton(listen_ip, &servaddr.sin_addr) == 0)
    {
        fprintf(stderr, "IP inválido para bind: %s\n", listen_ip);
        close(sockfd);
        return -1;
    }

    if (bind(sockfd, (struct sockaddr *)&servaddr, sizeof(servaddr)) < 0)
    {
        perror("bind");
        close(sockfd);
        return -1;
    }

    printf("[SERVER] UDP iterativo ouvindo em %s:%d\n", listen_ip, port);
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
        perror("recvfrom");
        return -1;
    }

    printf("[SERVER] Recebido %zd bytes de %s:%d — ecoando de volta\n",
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

    return 0;
}

static void serve_forever(int sockfd)
{
    unsigned char buffer[MAX_BUFFER];
    while (1)
    {
        handle_one_packet(sockfd, buffer);
    }
}

int main(int argc, char *argv[])
{
    if (argc != 3)
    {
        fprintf(stderr, "Uso: %s <listen_ip> <port>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *listen_ip = argv[1];
    int port = atoi(argv[2]);

    int sockfd = setup_socket(listen_ip, port);
    if (sockfd < 0)
    {
        return EXIT_FAILURE;
    }

    serve_forever(sockfd);

    close(sockfd);
    return EXIT_SUCCESS;
}
