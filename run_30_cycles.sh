for cycle in {1..30}; do
  echo "=== Iniciando ciclo $cycle de 30 ==="

  ./client_udp 10.0.0.16 10.0.0.12 50000 1 &

  ./client_udp 10.0.0.17 10.0.0.12 50000 2 &

  wait

  echo "=== Ciclo $cycle concluído ==="
done

echo "Todos os 30 ciclos finalizaram."
