#!/bin/bash

SERVER_IP="10.0.0.12"
SERVER_PORT=9090

echo "=== Executando 100 ciclos de teste simultâneo ==="
echo "Servidor: $SERVER_IP:$SERVER_PORT"

for cycle in {1..100}; do
  echo "=== Iniciando ciclo $cycle de 100 ==="

  ./client_udp auto $SERVER_IP $SERVER_PORT 1 &
  PID1=$!

  ./client_udp auto $SERVER_IP $SERVER_PORT 2 &
  PID2=$!

  wait $PID1
  wait $PID2

  echo "=== Ciclo $cycle concluído ==="
  sleep 1
done

echo "Todos os 100 ciclos finalizaram."
