#!/bin/bash

SERVER_PORT=9090
CAPTURE_TIME=3600*2
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RAW_LOG="tcpdump_raw_${TIMESTAMP}.log"
ANALYSIS_LOG="tcpdump_analysis_${TIMESTAMP}.log"
PCAP_FILE="tcpdump_capture_${TIMESTAMP}.pcap"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== Análise de Pacotes UDP ===${NC}"
echo "Porta: $SERVER_PORT"
echo "Tempo de captura: ${CAPTURE_TIME}s"
echo "Arquivos de saída:"
echo "  - Raw: $RAW_LOG"
echo "  - Análise: $ANALYSIS_LOG"
echo "  - PCAP: $PCAP_FILE"
echo ""

capture_and_analyze() {
    echo -e "${YELLOW}Iniciando captura...${NC}"
    
    tcpdump -i any -n -w "$PCAP_FILE" udp port $SERVER_PORT 2>/dev/null &
    TCPDUMP_PID=$!
    
    timeout $CAPTURE_TIME tcpdump -i any -n -v -l udp port $SERVER_PORT 2>/dev/null | tee "$RAW_LOG" | \
    while read line; do

        if [[ $line =~ ([0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]+) ]]; then
            timestamp="${BASH_REMATCH[1]}"
        fi
        
        if [[ $line =~ ([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\.([0-9]+)\ \>\ ([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\.([0-9]+) ]]; then
            src_ip="${BASH_REMATCH[1]}"
            src_port="${BASH_REMATCH[2]}"
            dst_ip="${BASH_REMATCH[3]}"
            dst_port="${BASH_REMATCH[4]}"
        fi
        
        if [[ $line =~ "length "([0-9]+) ]]; then
            length="${BASH_REMATCH[1]}"
            echo -e "${timestamp} | ${src_ip}:${src_port} → ${dst_ip}:${dst_port} | ${GREEN}${length} bytes${NC}"
        fi
    done
    
    sleep $((CAPTURE_TIME + 1))
    kill $TCPDUMP_PID 2>/dev/null
}

generate_analysis() {
    echo -e "\n${YELLOW}Gerando análise detalhada...${NC}"
    
    {
        echo "=== ANÁLISE DE CAPTURA DE PACOTES UDP ==="
        echo "Data: $(date)"
        echo "Porta monitorada: $SERVER_PORT"
        echo "Duração da captura: ${CAPTURE_TIME}s"
        echo ""
        
        echo "=== ESTATÍSTICAS GERAIS ==="
        total_packets=$(grep -c "length" "$RAW_LOG" 2>/dev/null || echo "0")
        echo "Total de pacotes UDP capturados: $total_packets"
        echo ""
        
        echo "=== DISTRIBUIÇÃO POR TAMANHO ==="
        echo "Quantidade | Tamanho (bytes)"
        echo "----------------------------"
        grep -oE "length [0-9]+" "$RAW_LOG" 2>/dev/null | \
            sed 's/length //' | \
            sort -n | \
            uniq -c | \
            sort -k2 -n || echo "Nenhum pacote encontrado"
        
        echo ""
        echo "=== ESTATÍSTICAS POR TAMANHO ==="

        expected_sizes=(2 4 8 16 32 64 128 256 512 1024 2048 4096 8192 16384 32768 65507)
        
        for size in "${expected_sizes[@]}"; do
            count=$(grep -c "length $size\b" "$RAW_LOG" 2>/dev/null || echo "0")
            if [ "$count" -gt 0 ]; then
                echo "Tamanho $size bytes: $count pacotes"
            fi
        done
        
        echo ""
        echo "=== FLUXOS DE COMUNICAÇÃO ==="
        echo "Origem → Destino | Quantidade"
        echo "------------------------------"
        grep -E "[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+.*>" "$RAW_LOG" 2>/dev/null | \
            grep -oE "[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+ > [0-9]+\.[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+" | \
            sort | uniq -c | sort -rn | head -10 || echo "Nenhum fluxo encontrado"
        
        echo ""
        echo "=== ANÁLISE TEMPORAL ==="

        if [ -f "$RAW_LOG" ] && [ -s "$RAW_LOG" ]; then
            first_time=$(grep -m1 -oE "[0-9]{2}:[0-9]{2}:[0-9]{2}" "$RAW_LOG" 2>/dev/null || echo "00:00:00")
            last_time=$(grep -oE "[0-9]{2}:[0-9]{2}:[0-9]{2}" "$RAW_LOG" 2>/dev/null | tail -1 || echo "00:00:00")
            echo "Primeiro pacote: $first_time"
            echo "Último pacote: $last_time"
            
            if [ "$total_packets" -gt 0 ] && [ "$CAPTURE_TIME" -gt 0 ]; then
                rate=$(echo "scale=2; $total_packets / $CAPTURE_TIME" | bc 2>/dev/null || echo "0")
                echo "Taxa média: $rate pacotes/segundo"
            fi
        fi
        
        echo ""
        echo "=== POSSÍVEIS ANOMALIAS ==="

        unexpected=$(grep -oE "length [0-9]+" "$RAW_LOG" 2>/dev/null | \
            sed 's/length //' | \
            sort -n | uniq | \
            grep -vE "^(2|4|8|16|32|64|128|256|512|1024|2048|4096|8192|16384|32768|65507)$" || true)
        
        if [ -n "$unexpected" ]; then
            echo "Tamanhos inesperados detectados:"
            echo "$unexpected"
        else
            echo "Nenhum tamanho inesperado detectado"
        fi
        
        large_packets=$(grep -E "length (1[5-9][0-9]{2}|[2-9][0-9]{3}|[1-9][0-9]{4})" "$RAW_LOG" 2>/dev/null | wc -l || echo "0")
        if [ "$large_packets" -gt 0 ]; then
            echo ""
            echo "AVISO: $large_packets pacotes grandes (>1500 bytes) detectados"
            echo "Possível fragmentação IP ocorrendo"
        fi
        
    } > "$ANALYSIS_LOG"
    
    echo -e "${GREEN}Análise salva em: $ANALYSIS_LOG${NC}"
}

display_summary() {
    echo -e "\n${GREEN}=== RESUMO DA CAPTURA ===${NC}"
    
    if [ -f "$RAW_LOG" ]; then
        total=$(grep -c "length" "$RAW_LOG" 2>/dev/null || echo "0")
        echo "Total de pacotes: $total"
        
        echo -e "\n${YELLOW}Top 5 tamanhos mais frequentes:${NC}"
        grep -oE "length [0-9]+" "$RAW_LOG" 2>/dev/null | \
            sed 's/length //' | \
            sort | uniq -c | sort -rn | head -5 | \
            while read count size; do
                printf "%6d pacotes de %6d bytes\n" "$count" "$size"
            done || echo "Nenhum dado disponível"
    fi
}

main() {
    rm -f "$RAW_LOG" "$ANALYSIS_LOG" "$PCAP_FILE" 2>/dev/null
    
    capture_and_analyze
    
    generate_analysis
    
    display_summary
    
    echo -e "\n${GREEN}Captura concluída!${NC}"
    echo "Arquivos gerados:"
    echo "  - Dados brutos: $RAW_LOG"
    echo "  - Análise: $ANALYSIS_LOG"
    echo "  - PCAP: $PCAP_FILE"
    echo ""
    echo "Para análise adicional:"
    echo "  tcpdump -r $PCAP_FILE -n"
    echo "  wireshark $PCAP_FILE"
}

main