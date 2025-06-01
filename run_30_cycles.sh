#!/bin/bash

SERVER_IP="<IP_DO_SEU_WSL>"
SERVER_PORT=50000

echo "=== Executando 30 ciclos de teste simultâneo ==="
echo "Servidor: $SERVER_IP:$SERVER_PORT"

for cycle in {1..30}; do
  echo "=== Iniciando ciclo $cycle de 30 ==="

  ./client_udp auto $SERVER_IP $SERVER_PORT 1 &
  PID1=$!

  ./client_udp auto $SERVER_IP $SERVER_PORT 2 &
  PID2=$!

  wait $PID1
  wait $PID2

  echo "=== Ciclo $cycle concluído ==="
  sleep 1
done

echo "Todos os 30 ciclos finalizaram."
