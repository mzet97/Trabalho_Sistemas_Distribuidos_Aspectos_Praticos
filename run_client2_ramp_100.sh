#!/bin/bash

SERVER_IP="100.0.0.12"
SERVER_PORT=9090

echo "=== Executando 100 instâncias do Cliente 2 ==="
echo "Servidor: $SERVER_IP:$SERVER_PORT"

for i in {1..100}; do
  echo "Executando instância $i/100 do Cliente 2..."
  
  ./client_udp_ramp auto $SERVER_IP $SERVER_PORT 2 &
  
  if [ $? -ne 0 ]; then
    echo "Erro na instância $i do Cliente 2"
  fi
done

echo "Todas as 100 instâncias do Cliente 2 finalizaram."
