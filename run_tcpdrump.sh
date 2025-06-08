#!/bin/bash

SERVER_PORT=9090

echo "Iniciando captura de pacotes UDP..."
echo "Tamanho esperado | Tamanho capturado"
echo "-----------------------------------"

timeout 30 tcpdump -i any -n -l udp port 9090 2>/dev/null | \
while read line; do
    if [[ $line =~ "length "([0-9]+) ]]; then
        echo "Capturado: ${BASH_REMATCH[1]} bytes"
    fi
done | sort | uniq -c