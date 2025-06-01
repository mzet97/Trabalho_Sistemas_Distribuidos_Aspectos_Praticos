for i in {1..30}; do
  ./client_udp 10.0.100.11 10.0.100.12 50000 2 &
done

wait
echo "Todas as 30 instâncias do Cliente 2 finalizaram."
