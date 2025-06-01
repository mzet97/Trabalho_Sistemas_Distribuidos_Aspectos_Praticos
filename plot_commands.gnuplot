# plot_commands.gnuplot

set datafile separator ","
set terminal pngcairo size 1024,768 enhanced font "Arial,10"
set grid

# ---------------------------------------------------------
# Gráfico RTT vs Tamanho (Experimento 1)
# ---------------------------------------------------------
set output "rtt_vs_size_cliente1.png"
set title "RTT Médio vs Tamanho de Payload — Cliente 1"
set xlabel "Tamanho do Payload (bytes)"
set ylabel "RTT (ms)"
plot \
  "stats_cliente1.csv" skip 1 using 1:3 with linespoints lt rgb "blue"  lw 2 pt 7 title "Média", \
  ""                     skip 1 using 1:3:5 with yerrorbars    lt rgb "red"   lw 1 title "Desvio Padrão"

set output "rtt_vs_size_cliente2.png"
set title "RTT Médio vs Tamanho de Payload — Cliente 2"
set xlabel "Tamanho do Payload (bytes)"
set ylabel "RTT (ms)"
plot \
  "stats_cliente2.csv" skip 1 using 1:3 with linespoints lt rgb "green"  lw 2 pt 7 title "Média", \
  ""                     skip 1 using 1:3:5 with yerrorbars    lt rgb "magenta" lw 1 title "Desvio Padrão"


# ---------------------------------------------------------
# Gráficos RTT vs Nível de Rampa (Experimento 2)
# Apenas três tamanhos de payload: 2, 1024 e max (65507)
# ---------------------------------------------------------

# Cliente 1
set output "rtt_ramp_vs_level_cliente1.png"
set title "RTT Médio vs Nível (Rampa) — Cliente 1"
set xlabel "Nível da Rampa"
set ylabel "RTT (ms)"

# Definimos três tamanhos representativos:
#  - 2 bytes
#  - 1024 bytes
#  - MAX_UDP_PAYLOAD (=65507)
# Usamos uma expressão “($1 == tamanho ? $2 : 1/0)” para filtrar apenas as linhas com aquele tamanho.
plot \
  "stats_ramp_cliente1.csv" skip 1 using ($1==2      ? $2 : 1/0):($1==2      ? $4 : 1/0) with linespoints lt rgb "blue"    lw 2 pt 7 title "2 bytes", \
  "stats_ramp_cliente1.csv" skip 1 using ($1==1024   ? $2 : 1/0):($1==1024   ? $4 : 1/0) with linespoints lt rgb "orange"  lw 2 pt 7 title "1 KB", \
  "stats_ramp_cliente1.csv" skip 1 using ($1==65507  ? $2 : 1/0):($1==65507  ? $4 : 1/0) with linespoints lt rgb "purple"  lw 2 pt 7 title "65 507 bytes", \
  \
  ""                         skip 1 using ($1==2      ? $2 : 1/0):($1==2      ? $8:$9) with yerrorbars lt rgb "blue"   lw 1 title "IC (2 B)", \
  ""                         skip 1 using ($1==1024   ? $2 : 1/0):($1==1024   ? $8:$9) with yerrorbars lt rgb "orange" lw 1 title "IC (1 KB)", \
  ""                         skip 1 using ($1==65507  ? $2 : 1/0):($1==65507  ? $8:$9) with yerrorbars lt rgb "purple" lw 1 title "IC (65 507 B)"


# Cliente 2
set output "rtt_ramp_vs_level_cliente2.png"
set title "RTT Médio vs Nível (Rampa) — Cliente 2"
set xlabel "Nível da Rampa"
set ylabel "RTT (ms)"

plot \
  "stats_ramp_cliente2.csv" skip 1 using ($1==2      ? $2 : 1/0):($1==2      ? $4 : 1/0) with linespoints lt rgb "blue"    lw 2 pt 7 title "2 bytes", \
  "stats_ramp_cliente2.csv" skip 1 using ($1==1024   ? $2 : 1/0):($1==1024   ? $4 : 1/0) with linespoints lt rgb "orange"  lw 2 pt 7 title "1 KB", \
  "stats_ramp_cliente2.csv" skip 1 using ($1==65507  ? $2 : 1/0):($1==65507  ? $4 : 1/0) with linespoints lt rgb "purple"  lw 2 pt 7 title "65 507 bytes", \
  \
  ""                         skip 1 using ($1==2      ? $2 : 1/0):($1==2      ? $8:$9) with yerrorbars lt rgb "blue"   lw 1 title "IC (2 B)", \
  ""                         skip 1 using ($1==1024   ? $2 : 1/0):($1==1024   ? $8:$9) with yerrorbars lt rgb "orange" lw 1 title "IC (1 KB)", \
  ""                         skip 1 using ($1==65507  ? $2 : 1/0):($1==65507  ? $8:$9) with yerrorbars lt rgb "purple" lw 1 title "IC (65 507 B)"
