for cycle in {1..30}; do
  echo "=== Iniciando ciclo $cycle de 30 ==="

  ./client_udp 0.0.0.0 0.0.0.0 50000 1 &

  ./client_udp 0.0.0.0 0.0.0.0 50000 2 &

  wait

  echo "=== Ciclo $cycle concluído ==="
done

echo "Todos os 30 ciclos finalizaram."
