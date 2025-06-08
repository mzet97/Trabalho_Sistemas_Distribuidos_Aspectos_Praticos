#!/bin/bash

SERVER_IP="10.0.0.12"
SERVER_PORT=9090

echo "=== Executando 2 ciclos de teste de rampa simultâneo ==="
echo "Servidor: $SERVER_IP:$SERVER_PORT"

for cycle in {1..2}; do
  echo "=== Iniciando ciclo $cycle de 2 ==="

  ./client_udp_ramp auto $SERVER_IP $SERVER_PORT 1 &
  PID1=$!

  ./client_udp_ramp auto $SERVER_IP $SERVER_PORT 2 &
  PID2=$!

  wait $PID1
  wait $PID2

  echo "=== Ciclo $cycle concluído ==="
  sleep 2
done

echo "Todos os 2 ciclos finalizaram."
