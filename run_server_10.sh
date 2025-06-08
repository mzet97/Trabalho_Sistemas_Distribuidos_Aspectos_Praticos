#!/bin/bash

SERVER_IP="10.0.0.12"
SERVER_PORT=9090

echo "=== Executando o servidor 10 Mbs ==="
echo "Servidor: $SERVER_IP:$SERVER_PORT"

./server_udp $SERVER_IP $SERVER_PORT &
