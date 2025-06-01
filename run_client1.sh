for i in {1..30}; do
  ./client_udp 10.0.0.16 10.0.0.12 50000 1
done

wait
echo "Todas as 30 instâncias do Cliente 1 finalizaram."
