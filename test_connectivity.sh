#!/bin/bash

if [ $# -ne 2 ]; then
    echo "Uso: $0 <server_ip> <server_port>"
    exit 1
fi

SERVER_IP=$1
SERVER_PORT=$2

echo "=== Diagnóstico de Conectividade UDP ==="
echo "Servidor: $SERVER_IP:$SERVER_PORT"
echo

echo "1. Testando conectividade básica..."
ping -c 3 $SERVER_IP
echo

echo "2. Verificando rota para $SERVER_IP..."
ip route get $SERVER_IP
echo

echo "3. Interfaces de rede locais:"
ip addr show
echo

echo "4. Testando com netcat (timeout 5s)..."
echo "TEST_UDP" | timeout 5 nc -u $SERVER_IP $SERVER_PORT
echo

echo "5. Testando com cliente (1 iteração)..."
timeout 10 ./client_udp auto $SERVER_IP $SERVER_PORT 1
echo

echo "=== Fim do diagnóstico ==="
