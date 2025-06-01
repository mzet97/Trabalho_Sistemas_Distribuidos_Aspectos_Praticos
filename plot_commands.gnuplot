set datafile separator ","

set terminal pngcairo size 1024,768 enhanced font "Arial,10"
set grid

set output "rtt_vs_size_cliente1.png"
set title "RTT Médio vs Tamanho de Payload — Cliente 1"
set xlabel "Tamanho do Payload (bytes)"
set ylabel "RTT (ms)"
plot \
    "stats_cliente1.csv" skip 1 using 1:3 with linespoints lt rgb "blue"  lw 2 pt 7 title "Média", \
    ""                     skip 1 using 1:3:5 with yerrorbars lt rgb "red"   lw 1 title "Desvio Padrão"

set output "rtt_vs_size_cliente2.png"
set title "RTT Médio vs Tamanho de Payload — Cliente 2"
set xlabel "Tamanho do Payload (bytes)"
set ylabel "RTT (ms)"
plot \
    "stats_cliente2.csv" skip 1 using 1:3 with linespoints lt rgb "green"  lw 2 pt 7 title "Média", \
    ""                     skip 1 using 1:3:5 with yerrorbars lt rgb "magenta" lw 1 title "Desvio Padrão"

set output "rtt_ramp_vs_level_cliente1.png"
set title "RTT Médio vs Nível (Rampa) — Cliente 1"
set xlabel "Nível da Rampa"
set ylabel "RTT (ms)"
plot \
    "stats_ramp_cliente1.csv" skip 1 using 2:4 with linespoints lt rgb "blue"  lw 2 pt 7 title "Média", \
    ""                         skip 1 using 2:4:6 with yerrorbars lt rgb "red"   lw 1 title "Desvio Padrão"

set output "rtt_ramp_vs_level_cliente2.png"
set title "RTT Médio vs Nível (Rampa) — Cliente 2"
set xlabel "Nível da Rampa"
set ylabel "RTT (ms)"
plot \
    "stats_ramp_cliente2.csv" skip 1 using 2:4 with linespoints lt rgb "green"  lw 2 pt 7 title "Média", \
    ""                         skip 1 using 2:4:6 with yerrorbars lt rgb "magenta" lw 1 title "Desvio Padrão"
