for cycle in {1..2}; do
  echo "=== Iniciando ciclo $cycle de 2 ==="

  ./client_udp_ramp 10.0.0.16 10.0.0.12 50000 1 &

  ./client_udp_ramp 10.0.0.14 10.0.0.12 50000 2 &

  wait

  echo "=== Ciclo $cycle concluído ==="
done

echo "Todos os 2 ciclos finalizaram."
