#!/bin/bash

SERVER_IP="10.0.0.12"
SERVER_PORT=9090

echo "=== Executando 100 instâncias do Cliente 1 ==="
echo "Servidor: $SERVER_IP:$SERVER_PORT"

for i in {1..100}; do
  echo "Executando instância $i/100 do Cliente 1..."
  
  ./client_udp_ramp auto $SERVER_IP $SERVER_PORT 1
  
  if [ $? -ne 0 ]; then
    echo "Erro na instância $i do Cliente 1"
  fi
done

echo "Todas as 100 instâncias do Cliente 1 finalizaram."
