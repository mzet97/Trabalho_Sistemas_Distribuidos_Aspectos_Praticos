for cycle in {1..2}; do
  echo "=== Iniciando ciclo $cycle de 2 ==="

  ./client_udp_ramp 0.0.0.0 0.0.0.0 50000 1 &

  ./client_udp_ramp 0.0.0.0 0.0.0.0 50000 2 &

  wait

  echo "=== Ciclo $cycle concluído ==="
done

echo "Todos os 2 ciclos finalizaram."
