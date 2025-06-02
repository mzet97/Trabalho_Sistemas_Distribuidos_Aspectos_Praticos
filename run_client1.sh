#!/bin/bash

SERVER_IP="<IP_DO_SEU_WSL>"
SERVER_PORT=50000

echo "=== Executando 30 instâncias do Cliente 1 ==="
echo "Servidor: $SERVER_IP:$SERVER_PORT"

for i in {1..30}; do
  echo "Executando instância $i/30 do Cliente 1..."
  # Usar 'auto' em vez de IP específico para evitar problemas de bind
  ./client_udp auto $SERVER_IP $SERVER_PORT 1
  
  if [ $? -ne 0 ]; then
    echo "Erro na instância $i do Cliente 1"
  fi
done

echo "Todas as 30 instâncias do Cliente 1 finalizaram."
