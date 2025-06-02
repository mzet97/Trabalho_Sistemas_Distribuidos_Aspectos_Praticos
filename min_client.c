#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <errno.h>

#define SERVER_IP "152.92.236.12" // IP do seu servidor
#define PORT 50000                // Porta do seu servidor
#define BUFSIZE 1024

int main()
{
    int sockfd;
    struct sockaddr_in servaddr;
    char buffer[BUFSIZE];
    char message[] = "Ola do cliente minimo!";

    if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0)
    {
        perror("socket creation failed");
        exit(EXIT_FAILURE);
    }

    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(PORT);
    if (inet_aton(SERVER_IP, &servaddr.sin_addr) == 0)
    {
        fprintf(stderr, "inet_aton failed for IP: %s\n", SERVER_IP);
        close(sockfd);
        exit(EXIT_FAILURE);
    }

    printf("Enviando para %s:%d: '%s'\n", SERVER_IP, PORT, message);
    ssize_t sent_len = sendto(sockfd, message, strlen(message), 0, (const struct sockaddr *)&servaddr, sizeof(servaddr));
    if (sent_len < 0)
    {
        perror("sendto failed");
        fprintf(stderr, "Erro no sendto: %s (errno: %d)\n", strerror(errno), errno);
        close(sockfd);
        exit(EXIT_FAILURE);
    }
    printf("%zd bytes enviados.\n", sent_len);

    // Configurar timeout para recvfrom
    struct timeval tv;
    tv.tv_sec = 5; // 5 segundos de timeout
    tv.tv_usec = 0;
    if (setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, (const char *)&tv, sizeof tv) < 0)
    {
        perror("setsockopt SO_RCVTIMEO failed");
    }

    printf("Aguardando resposta...\n");
    socklen_t len = sizeof(servaddr); // Reusar servaddr não é ideal para guardar de quem veio, mas ok para teste simples
    ssize_t n = recvfrom(sockfd, buffer, BUFSIZE, 0, (struct sockaddr *)&servaddr, &len);

    if (n < 0)
    {
        perror("recvfrom failed");
        fprintf(stderr, "Erro no recvfrom: %s (errno: %d)\n", strerror(errno), errno);
        if (errno == EAGAIN || errno == EWOULDBLOCK)
        {
            printf("Timeout! Nenhuma resposta do servidor.\n");
        }
    }
    else
    {
        buffer[n] = '\0';
        printf("Servidor respondeu: %s\n", buffer);
    }

    close(sockfd);
    return 0;
}