set datafile separator ","
set terminal pngcairo size 1024,768 enhanced font "Arial,10"
set grid

set output "rtt_vs_size_cliente1_detailed.png"
set title "RTT vs Tamanho de Payload — Cliente 1 (com IC 98% e Percentis)"
set xlabel "Tamanho do Payload (bytes)"
set ylabel "RTT (ms)"
set key left top

plot \
  "stats_cliente1.csv" skip 1 using 1:3 with linespoints lt rgb "blue" lw 2 pt 7 title "Média", \
  ""                   skip 1 using 1:3:($7):($8) with yerrorbars lt rgb "blue" lw 1 title "IC 98%", \
  ""                   skip 1 using 1:9 with lines lt rgb "orange" lw 1 dt 2 title "P95", \
  ""                   skip 1 using 1:10 with lines lt rgb "red" lw 1 dt 3 title "P99"

set output "rtt_vs_size_cliente2_detailed.png"
set title "RTT vs Tamanho de Payload — Cliente 2 (com IC 98% e Percentis)"
plot \
  "stats_cliente2.csv" skip 1 using 1:3 with linespoints lt rgb "green" lw 2 pt 7 title "Média", \
  ""                   skip 1 using 1:3:($7):($8) with yerrorbars lt rgb "green" lw 1 title "IC 98%", \
  ""                   skip 1 using 1:9 with lines lt rgb "orange" lw 1 dt 2 title "P95", \
  ""                   skip 1 using 1:10 with lines lt rgb "red" lw 1 dt 3 title "P99"

set output "loss_rate_vs_size.png"
set title "Taxa de Perda vs Tamanho de Payload"
set xlabel "Tamanho do Payload (bytes)"
set ylabel "Taxa de Perda (%)"
set yrange [0:*]

plot \
  "stats_cliente1.csv" skip 1 using 1:13 with linespoints lt rgb "blue" lw 2 pt 7 title "Cliente 1 (10 Mbps)", \
  "stats_cliente2.csv" skip 1 using 1:13 with linespoints lt rgb "green" lw 2 pt 5 title "Cliente 2 (100 Mbps)"

set output "jitter_vs_size.png"
set title "Jitter Médio vs Tamanho de Payload"
set xlabel "Tamanho do Payload (bytes)"
set ylabel "Jitter (ms)"
set yrange [0:*]

plot \
  "stats_cliente1.csv" skip 1 using 1:6 with linespoints lt rgb "blue" lw 2 pt 7 title "Cliente 1 (10 Mbps)", \
  "stats_cliente2.csv" skip 1 using 1:6 with linespoints lt rgb "green" lw 2 pt 5 title "Cliente 2 (100 Mbps)"

set output "rtt_ramp_vs_level_cliente1_detailed.png"
set title "RTT vs Nível de Rampa — Cliente 1"
set xlabel "Nível da Rampa"
set ylabel "RTT (ms)"
set xrange [1:19]
set key right top

# Plotamos para três tamanhos representativos
plot \
  "stats_ramp_cliente1.csv" skip 1 using ($1==2 ? $2 : 1/0):($1==2 ? $4 : 1/0) \
    with linespoints lt rgb "blue" lw 2 pt 7 title "2 bytes (média)", \
  "" skip 1 using ($1==2 ? $2 : 1/0):($1==2 ? $10 : 1/0) \
    with lines lt rgb "blue" lw 1 dt 2 title "2 bytes (P95)", \
  \
  "" skip 1 using ($1==1024 ? $2 : 1/0):($1==1024 ? $4 : 1/0) \
    with linespoints lt rgb "orange" lw 2 pt 7 title "1KB (média)", \
  "" skip 1 using ($1==1024 ? $2 : 1/0):($1==1024 ? $10 : 1/0) \
    with lines lt rgb "orange" lw 1 dt 2 title "1KB (P95)", \
  \
  "" skip 1 using ($1==65507 ? $2 : 1/0):($1==65507 ? $4 : 1/0) \
    with linespoints lt rgb "purple" lw 2 pt 7 title "64KB (média)", \
  "" skip 1 using ($1==65507 ? $2 : 1/0):($1==65507 ? $10 : 1/0) \
    with lines lt rgb "purple" lw 1 dt 2 title "64KB (P95)"

set output "rtt_ramp_vs_level_cliente2_detailed.png"
set title "RTT vs Nível de Rampa — Cliente 2"

plot \
  "stats_ramp_cliente2.csv" skip 1 using ($1==2 ? $2 : 1/0):($1==2 ? $4 : 1/0) \
    with linespoints lt rgb "blue" lw 2 pt 7 title "2 bytes (média)", \
  "" skip 1 using ($1==2 ? $2 : 1/0):($1==2 ? $10 : 1/0) \
    with lines lt rgb "blue" lw 1 dt 2 title "2 bytes (P95)", \
  \
  "" skip 1 using ($1==1024 ? $2 : 1/0):($1==1024 ? $4 : 1/0) \
    with linespoints lt rgb "orange" lw 2 pt 7 title "1KB (média)", \
  "" skip 1 using ($1==1024 ? $2 : 1/0):($1==1024 ? $10 : 1/0) \
    with lines lt rgb "orange" lw 1 dt 2 title "1KB (P95)", \
  \
  "" skip 1 using ($1==65507 ? $2 : 1/0):($1==65507 ? $4 : 1/0) \
    with linespoints lt rgb "purple" lw 2 pt 7 title "64KB (média)", \
  "" skip 1 using ($1==65507 ? $2 : 1/0):($1==65507 ? $10 : 1/0) \
    with lines lt rgb "purple" lw 1 dt 2 title "64KB (P95)"

set output "loss_rate_ramp.png"
set title "Taxa de Perda vs Nível de Rampa"
set xlabel "Nível da Rampa"
set ylabel "Taxa de Perda (%)"
set xrange [1:19]
set yrange [0:*]

plot \
  "stats_ramp_cliente1.csv" skip 1 using ($1==1024 ? $2 : 1/0):($1==1024 ? $14 : 1/0) \
    with linespoints lt rgb "blue" lw 2 pt 7 title "Cliente 1 - 1KB", \
  "stats_ramp_cliente2.csv" skip 1 using ($1==1024 ? $2 : 1/0):($1==1024 ? $14 : 1/0) \
    with linespoints lt rgb "green" lw 2 pt 5 title "Cliente 2 - 1KB", \
  "stats_ramp_cliente1.csv" skip 1 using ($1==65507 ? $2 : 1/0):($1==65507 ? $14 : 1/0) \
    with linespoints lt rgb "red" lw 2 pt 7 title "Cliente 1 - 64KB", \
  "stats_ramp_cliente2.csv" skip 1 using ($1==65507 ? $2 : 1/0):($1==65507 ? $14 : 1/0) \
    with linespoints lt rgb "magenta" lw 2 pt 5 title "Cliente 2 - 64KB"

set output "percentiles_comparison.png"
set title "Comparação de Percentis P95 e P99"
set xlabel "Tamanho do Payload (bytes)"
set ylabel "RTT (ms)"
set logscale x 2
set key left top

plot \
  "stats_cliente1.csv" skip 1 using 1:9 with linespoints lt rgb "blue" lw 2 pt 7 title "Cliente 1 - P95", \
  ""                   skip 1 using 1:10 with linespoints lt rgb "blue" lw 2 pt 5 dt 2 title "Cliente 1 - P99", \
  "stats_cliente2.csv" skip 1 using 1:9 with linespoints lt rgb "green" lw 2 pt 7 title "Cliente 2 - P95", \
  ""                   skip 1 using 1:10 with linespoints lt rgb "green" lw 2 pt 5 dt 2 title "Cliente 2 - P99"

set output "outliers_histogram.png"
set title "Número de Outliers por Tamanho de