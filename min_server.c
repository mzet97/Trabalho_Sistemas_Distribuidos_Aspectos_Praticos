#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define PORT 50000 // Use a sua porta
#define BUFSIZE 1024

int main()
{
    int sockfd;
    struct sockaddr_in servaddr, cliaddr;
    char buffer[BUFSIZE];
    socklen_t len;

    if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0)
    {
        perror("socket creation failed");
        exit(EXIT_FAILURE);
    }

    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = INADDR_ANY; // Escuta em todos os IPs
    servaddr.sin_port = htons(PORT);

    if (bind(sockfd, (const struct sockaddr *)&servaddr, sizeof(servaddr)) < 0)
    {
        perror("bind failed");
        close(sockfd);
        exit(EXIT_FAILURE);
    }
    printf("Servidor UDP escutando na porta %d\n", PORT);

    while (1)
    {
        len = sizeof(cliaddr);
        printf("Aguardando mensagem...\n");
        ssize_t n = recvfrom(sockfd, buffer, BUFSIZE, 0, (struct sockaddr *)&cliaddr, &len);
        if (n < 0)
        {
            perror("recvfrom error");
            continue;
        }
        buffer[n] = '\0';
        printf("Cliente [%s:%d] disse: %s\n", inet_ntoa(cliaddr.sin_addr), ntohs(cliaddr.sin_port), buffer);

        sendto(sockfd, buffer, n, 0, (const struct sockaddr *)&cliaddr, len);
        printf("Ecoado de volta para o cliente.\n");
    }
    close(sockfd);
    return 0;
}