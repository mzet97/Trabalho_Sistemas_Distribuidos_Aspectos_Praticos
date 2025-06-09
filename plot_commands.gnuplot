# plot_commands_improved.gnuplot
# Geração completa de todos os gráficos especificados

set datafile separator ","
set terminal pngcairo size 1200,800 enhanced font "Arial,12"
set grid
set key outside right top

# Função para verificar existência de arquivo
file_exists(filename) = system("test -f " . filename . " && echo 1 || echo 0") + 0

print "=== Iniciando geração de gráficos ==="
print ""

# ---------------------------------------------------------
# 1. rtt_cliente1_10mbps.png
# ---------------------------------------------------------
if (file_exists("stats_cliente1.csv")) {
    print "Gerando: rtt_cliente1_10mbps.png"
    set output "rtt_cliente1_10mbps.png"
    set title "RTT vs Tamanho de Payload - Cliente 1 (Rede 10 Mbps)" font ",14"
    set xlabel "Tamanho do Payload (bytes)" font ",12"
    set ylabel "RTT (ms)" font ",12"
    set logscale x 2
    set format x "%.0f"
    set xtics rotate by -45
    set yrange [0:*]
    
    plot \
      "stats_cliente1.csv" skip 1 using 1:3 with linespoints \
        lt rgb "#0066CC" lw 3 pt 7 ps 1.2 title "RTT Médio", \
      "" skip 1 using 1:3:7:8 with yerrorbars \
        lt rgb "#0066CC" lw 1.5 pt 7 ps 0.8 title "IC 98%", \
      "" skip 1 using 1:9 with lines \
        lt rgb "#FF6600" lw 2 dt 2 title "Percentil 95", \
      "" skip 1 using 1:10 with lines \
        lt rgb "#CC0000" lw 2 dt 3 title "Percentil 99"
    
    unset logscale x
}

# ---------------------------------------------------------
# 2. rtt_cliente1_100mbps.png
# ---------------------------------------------------------
if (file_exists("stats_cliente1_100.csv")) {
    print "Gerando: rtt_cliente1_100mbps.png"
    set output "rtt_cliente1_100mbps.png"
    set title "RTT vs Tamanho de Payload - Cliente 1 (Rede 100 Mbps)" font ",14"
    set xlabel "Tamanho do Payload (bytes)" font ",12"
    set ylabel "RTT (ms)" font ",12"
    set logscale x 2
    set format x "%.0f"
    set xtics rotate by -45
    set yrange [0:*]
    
    plot \
      "stats_cliente1_100.csv" skip 1 using 1:3 with linespoints \
        lt rgb "#009900" lw 3 pt 7 ps 1.2 title "RTT Médio", \
      "" skip 1 using 1:3:7:8 with yerrorbars \
        lt rgb "#009900" lw 1.5 pt 7 ps 0.8 title "IC 98%", \
      "" skip 1 using 1:9 with lines \
        lt rgb "#FF9900" lw 2 dt 2 title "Percentil 95", \
      "" skip 1 using 1:10 with lines \
        lt rgb "#CC3300" lw 2 dt 3 title "Percentil 99"
    
    unset logscale x
}

# ---------------------------------------------------------
# 3. network_comparison_rtt.png
# ---------------------------------------------------------
if (file_exists("stats_network_10mbps.csv") && file_exists("stats_network_100mbps.csv")) {
    print "Gerando: network_comparison_rtt.png"
    set output "network_comparison_rtt.png"
    set title "Comparação de RTT Médio: 10 Mbps vs 100 Mbps" font ",16"
    set xlabel "Tamanho do Payload (bytes)" font ",12"
    set ylabel "RTT Médio (ms)" font ",12"
    set logscale x 2
    set format x "%.0f"
    set xtics rotate by -45
    set yrange [0:*]
    set key inside left top
    
    plot \
      "stats_network_10mbps.csv" skip 1 using 1:2 with linespoints \
        lt rgb "#CC0000" lw 3 pt 7 ps 1.2 title "Rede 10 Mbps", \
      "stats_network_100mbps.csv" skip 1 using 1:2 with linespoints \
        lt rgb "#009900" lw 3 pt 5 ps 1.2 title "Rede 100 Mbps"
}

# ---------------------------------------------------------
# 4. network_comparison_loss.png
# ---------------------------------------------------------
if (file_exists("stats_network_10mbps.csv") && file_exists("stats_network_100mbps.csv")) {
    print "Gerando: network_comparison_loss.png"
    set output "network_comparison_loss.png"
    set title "Comparação de Taxa de Perda: 10 Mbps vs 100 Mbps" font ",16"
    set xlabel "Tamanho do Payload (bytes)" font ",12"
    set ylabel "Taxa de Perda (%)" font ",12"
    set logscale x 2
    set format x "%.0f"
    set xtics rotate by -45
    set yrange [0:100]
    set key inside right top
    
    plot \
      "stats_network_10mbps.csv" skip 1 using 1:7 with linespoints \
        lt rgb "#CC0000" lw 3 pt 7 ps 1.2 title "Rede 10 Mbps", \
      "stats_network_100mbps.csv" skip 1 using 1:7 with linespoints \
        lt rgb "#009900" lw 3 pt 5 ps 1.2 title "Rede 100 Mbps"
}

# ---------------------------------------------------------
# 5. network_comparison_jitter.png
# ---------------------------------------------------------
if (file_exists("stats_network_10mbps.csv") && file_exists("stats_network_100mbps.csv")) {
    print "Gerando: network_comparison_jitter.png"
    set output "network_comparison_jitter.png"
    set title "Comparação de Jitter Médio: 10 Mbps vs 100 Mbps" font ",16"
    set xlabel "Tamanho do Payload (bytes)" font ",12"
    set ylabel "Jitter Médio (ms)" font ",12"
    set logscale x 2
    set format x "%.0f"
    set xtics rotate by -45
    set yrange [0:*]
    set key inside left top
    
    plot \
      "stats_network_10mbps.csv" skip 1 using 1:6 smooth csplines \
        lt rgb "#CC0000" lw 3 title "Rede 10 Mbps", \
      "stats_network_100mbps.csv" skip 1 using 1:6 smooth csplines \
        lt rgb "#009900" lw 3 title "Rede 100 Mbps", \
      "stats_network_10mbps.csv" skip 1 using 1:6 with points \
        lt rgb "#CC0000" pt 7 ps 0.8 notitle, \
      "stats_network_100mbps.csv" skip 1 using 1:6 with points \
        lt rgb "#009900" pt 5 ps 0.8 notitle
}

# ---------------------------------------------------------
# 6. network_comparison_percentiles.png
# ---------------------------------------------------------
if (file_exists("stats_network_10mbps.csv") && file_exists("stats_network_100mbps.csv")) {
    print "Gerando: network_comparison_percentiles.png"
    set output "network_comparison_percentiles.png"
    set title "Comparação de Percentis P95 e P99" font ",16"
    set xlabel "Tamanho do Payload (bytes)" font ",12"
    set ylabel "RTT (ms)" font ",12"
    set logscale x 2
    set format x "%.0f"
    set xtics rotate by -45
    set yrange [0:*]
    set key inside left top
    
    plot \
      "stats_network_10mbps.csv" skip 1 using 1:4 with lines \
        lt rgb "#CC0000" lw 3 dt 1 title "10 Mbps - P95", \
      "" skip 1 using 1:5 with lines \
        lt rgb "#CC0000" lw 3 dt 2 title "10 Mbps - P99", \
      "stats_network_100mbps.csv" skip 1 using 1:4 with lines \
        lt rgb "#009900" lw 3 dt 1 title "100 Mbps - P95", \
      "" skip 1 using 1:5 with lines \
        lt rgb "#009900" lw 3 dt 2 title "100 Mbps - P99"
}

# ---------------------------------------------------------
# 7. network_dashboard.png
# ---------------------------------------------------------
if (file_exists("stats_network_10mbps.csv") && file_exists("stats_network_100mbps.csv")) {
    print "Gerando: network_dashboard.png"
    set terminal pngcairo size 1600,1200 enhanced font "Arial,11"
    set output "network_dashboard.png"
    
    set multiplot layout 3,2 title "Dashboard Comparativo: Rede 10 Mbps vs 100 Mbps" font ",18"
    
    # 1. RTT Médio
    set title "RTT Médio por Tamanho"
    set xlabel "Tamanho (bytes)"
    set ylabel "RTT (ms)"
    set logscale x 2
    set format x "%.0f"
    set xtics rotate by -45
    set yrange [0:*]
    set key inside left top
    
    plot \
      "stats_network_10mbps.csv" skip 1 using 1:2 with linespoints \
        lt rgb "#CC0000" lw 2 pt 7 ps 0.8 title "10 Mbps", \
      "stats_network_100mbps.csv" skip 1 using 1:2 with linespoints \
        lt rgb "#009900" lw 2 pt 5 ps 0.8 title "100 Mbps"
    
    # 2. Taxa de Perda
    set title "Taxa de Perda"
    set ylabel "Perda (%)"
    set yrange [0:100]
    
    plot \
      "stats_network_10mbps.csv" skip 1 using 1:7 with linespoints \
        lt rgb "#CC0000" lw 2 pt 7 ps 0.8 title "10 Mbps", \
      "stats_network_100mbps.csv" skip 1 using 1:7 with linespoints \
        lt rgb "#009900" lw 2 pt 5 ps 0.8 title "100 Mbps"
    
    # 3. Jitter
    set title "Jitter"
    set ylabel "Jitter (ms)"
    set yrange [0:*]
    
    plot \
      "stats_network_10mbps.csv" skip 1 using 1:6 with linespoints \
        lt rgb "#CC0000" lw 2 pt 7 ps 0.8 title "10 Mbps", \
      "stats_network_100mbps.csv" skip 1 using 1:6 with linespoints \
        lt rgb "#009900" lw 2 pt 5 ps 0.8 title "100 Mbps"
    
    # 4. Percentil 95
    set title "Percentil 95"
    set ylabel "P95 (ms)"
    
    plot \
      "stats_network_10mbps.csv" skip 1 using 1:4 with linespoints \
        lt rgb "#CC0000" lw 2 pt 7 ps 0.8 title "10 Mbps", \
      "stats_network_100mbps.csv" skip 1 using 1:4 with linespoints \
        lt rgb "#009900" lw 2 pt 5 ps 0.8 title "100 Mbps"
    
    # 5. Percentil 99
    set title "Percentil 99"
    set ylabel "P99 (ms)"
    
    plot \
      "stats_network_10mbps.csv" skip 1 using 1:5 with linespoints \
        lt rgb "#CC0000" lw 2 pt 7 ps 0.8 title "10 Mbps", \
      "stats_network_100mbps.csv" skip 1 using 1:5 with linespoints \
        lt rgb "#009900" lw 2 pt 5 ps 0.8 title "100 Mbps"
    
    # 6. Speedup (Razão)
    set title "Speedup: RTT(10Mbps) / RTT(100Mbps)"
    set ylabel "Razão"
    set yrange [0:*]
    
    plot \
      "< paste -d, stats_network_10mbps.csv stats_network_100mbps.csv | tail -n +2" \
        using 1:($2/$10) with linespoints \
        lt rgb "#6600CC" lw 2 pt 7 ps 0.8 title "Speedup"
    
    unset multiplot
    set terminal pngcairo size 1200,800 enhanced font "Arial,12"
}

# ---------------------------------------------------------
# 8. cliente1_network_comparison.png
# ---------------------------------------------------------
if (file_exists("stats_cliente1.csv") && file_exists("stats_cliente1_100.csv")) {
    print "Gerando: cliente1_network_comparison.png"
    set output "cliente1_network_comparison.png"
    set title "Cliente 1: Comparação entre Redes 10 e 100 Mbps" font ",16"
    set xlabel "Tamanho do Payload (bytes)" font ",12"
    set ylabel "RTT Médio (ms)" font ",12"
    set logscale x 2
    set format x "%.0f"
    set xtics rotate by -45
    set yrange [0:*]
    set key inside left top
    
    plot \
      "stats_cliente1.csv" skip 1 using 1:3:7:8 with yerrorbars \
        lt rgb "#CC0000" lw 2 pt 7 ps 1 title "10 Mbps (IC 98%)", \
      "stats_cliente1_100.csv" skip 1 using 1:3:7:8 with yerrorbars \
        lt rgb "#009900" lw 2 pt 5 ps 1 title "100 Mbps (IC 98%)"
}

# ---------------------------------------------------------
# 9. cliente2_network_comparison.png
# ---------------------------------------------------------
if (file_exists("stats_cliente2.csv") && file_exists("stats_cliente2_100.csv")) {
    print "Gerando: cliente2_network_comparison.png"
    set output "cliente2_network_comparison.png"
    set title "Cliente 2: Comparação entre Redes 10 e 100 Mbps" font ",16"
    set xlabel "Tamanho do Payload (bytes)" font ",12"
    set ylabel "RTT Médio (ms)" font ",12"
    set logscale x 2
    set format x "%.0f"
    set xtics rotate by -45
    set yrange [0:*]
    set key inside left top
    
    plot \
      "stats_cliente2.csv" skip 1 using 1:3:7:8 with yerrorbars \
        lt rgb "#CC0000" lw 2 pt 7 ps 1 title "10 Mbps (IC 98%)", \
      "stats_cliente2_100.csv" skip 1 using 1:3:7:8 with yerrorbars \
        lt rgb "#009900" lw 2 pt 5 ps 1 title "100 Mbps (IC 98%)"
}

# ---------------------------------------------------------
# 10. ramp_cliente1_network_comparison.png
# ---------------------------------------------------------
unset logscale x
set xrange [1:19]
set format x "%.0f"
set xtics 1,1,19 rotate by 0

if (file_exists("stats_ramp_cliente1.csv") && file_exists("stats_ramp_cliente1_100.csv")) {
    print "Gerando: ramp_cliente1_network_comparison.png"
    set output "ramp_cliente1_network_comparison.png"
    set title "Rampa - Cliente 1: RTT vs Nível de Carga (1KB)" font ",16"
    set xlabel "Nível da Rampa (1=10 req/s → 10=100 req/s → 19=10 req/s)" font ",12"
    set ylabel "RTT Médio (ms)" font ",12"
    set key outside right top
    set yrange [0:*]
    
    plot \
      "stats_ramp_cliente1.csv" skip 1 using ($1==1024 ? $2 : 1/0):($1==1024 ? $4 : 1/0) \
        smooth csplines lt rgb "#CC0000" lw 3 title "10 Mbps (suavizado)", \
      "" skip 1 using ($1==1024 ? $2 : 1/0):($1==1024 ? $4 : 1/0) \
        with points lt rgb "#CC0000" pt 7 ps 0.8 title "10 Mbps (pontos)", \
      \
      "stats_ramp_cliente1_100.csv" skip 1 using ($1==1024 ? $2 : 1/0):($1==1024 ? $4 : 1/0) \
        smooth csplines lt rgb "#009900" lw 3 title "100 Mbps (suavizado)", \
      "" skip 1 using ($1==1024 ? $2 : 1/0):($1==1024 ? $4 : 1/0) \
        with points lt rgb "#009900" pt 5 ps 0.8 title "100 Mbps (pontos)"
}

# ---------------------------------------------------------
# 11. ramp_loss_network_comparison.png
# ---------------------------------------------------------
if (file_exists("stats_ramp_cliente1.csv") && file_exists("stats_ramp_cliente1_100.csv")) {
    print "Gerando: ramp_loss_network_comparison.png"
    set output "ramp_loss_network_comparison.png"
    set title "Taxa de Perda vs Nível de Rampa - Cliente 1" font ",16"
    set xlabel "Nível da Rampa" font ",12"
    set ylabel "Taxa de Perda (%)" font ",12"
    set yrange [0:100]
    
    plot \
      "stats_ramp_cliente1.csv" skip 1 using ($1==1024 ? $2 : 1/0):($1==1024 ? $14 : 1/0) \
        with linespoints lt rgb "#CC0000" lw 2 pt 7 title "10 Mbps - 1KB", \
      "stats_ramp_cliente1_100.csv" skip 1 using ($1==1024 ? $2 : 1/0):($1==1024 ? $14 : 1/0) \
        with linespoints lt rgb "#009900" lw 2 pt 5 title "100 Mbps - 1KB", \
      "stats_ramp_cliente1.csv" skip 1 using ($1==65507 ? $2 : 1/0):($1==65507 ? $14 : 1/0) \
        with linespoints lt rgb "#CC6666" lw 2 pt 7 dt 2 title "10 Mbps - 64KB", \
      "stats_ramp_cliente1_100.csv" skip 1 using ($1==65507 ? $2 : 1/0):($1==65507 ? $14 : 1/0) \
        with linespoints lt rgb "#66CC66" lw 2 pt 5 dt 2 title "100 Mbps - 64KB"
}

# ---------------------------------------------------------
# 12. saturation_analysis.png
# ---------------------------------------------------------
if (file_exists("stats_ramp_cliente1.csv") && file_exists("stats_ramp_cliente1_100.csv")) {
    print "Gerando: saturation_analysis.png"
    set output "saturation_analysis.png"
    set title "Análise de Saturação: RTT Normalizado por Nível" font ",16"
    set xlabel "Nível da Rampa" font ",12"
    set ylabel "RTT Normalizado (RTT/RTT_inicial)" font ",12"
    set yrange [0.5:5]
    set key outside right center
    
    # Linha de referência para saturação (150%)
    set arrow from 1,1.5 to 19,1.5 nohead lt rgb "#000000" lw 2 dt 2
    set label "Limiar de Saturação (150%)" at 10,1.6 center
    
    plot \
      "< awk -F, 'NR>1 && $1==2 {if(NR==2) base=$4; print $2,$4/base}' stats_ramp_cliente1.csv" \
        using 1:2 smooth csplines lt rgb "#FF0000" lw 2 title "10 Mbps - 2 bytes", \
      "< awk -F, 'NR>1 && $1==2 {if(NR==2) base=$4; print $2,$4/base}' stats_ramp_cliente1_100.csv" \
        using 1:2 smooth csplines lt rgb "#00FF00" lw 2 title "100 Mbps - 2 bytes", \
      \
      "< awk -F, 'NR>1 && $1==1024 {if($2==1) base=$4; print $2,$4/base}' stats_ramp_cliente1.csv" \
        using 1:2 smooth csplines lt rgb "#CC0000" lw 2 dt 2 title "10 Mbps - 1KB", \
      "< awk -F, 'NR>1 && $1==1024 {if($2==1) base=$4; print $2,$4/base}' stats_ramp_cliente1_100.csv" \
        using 1:2 smooth csplines lt rgb "#009900" lw 2 dt 2 title "100 Mbps - 1KB", \
      \
      "< awk -F, 'NR>1 && $1==65507 {if($2==1) base=$4; print $2,$4/base}' stats_ramp_cliente1.csv" \
        using 1:2 smooth csplines lt rgb "#990000" lw 2 dt 3 title "10 Mbps - 64KB", \
      "< awk -F, 'NR>1 && $1==65507 {if($2==1) base=$4; print $2,$4/base}' stats_ramp_cliente1_100.csv" \
        using 1:2 smooth csplines lt rgb "#006600" lw 2 dt 3 title "100 Mbps - 64KB"
    
    unset arrow
    unset label
}

print ""
print "=== Geração de gráficos concluída ==="
print ""

# Listar arquivos gerados
system("echo 'Arquivos PNG gerados:'; ls -la *.png 2>/dev/null | grep -E '(rtt_|network_|cliente[12]_|ramp_|saturation).*\.png' | awk '{print \"  - \" $9}' || echo '  Nenhum arquivo gerado'")