#!/bin/bash

if [ $# -ne 2 ]; then
    echo "Uso: $0 <server_ip> <server_port>"
    exit 1
fi

SERVER_IP=$1
SERVER_PORT=$2

echo "=== 🔍 DIAGNÓSTICO COMPLETO DE CONECTIVIDADE UDP ==="
echo "Servidor: $SERVER_IP:$SERVER_PORT"
echo "Timestamp: $(date)"
echo

echo "1. 🌐 Testando conectividade básica de rede..."
ping -c 3 -W 3 $SERVER_IP
PING_RESULT=$?
if [ $PING_RESULT -ne 0 ]; then
    echo "❌ PING FALHOU - Verifique conectividade de rede"
else
    echo "✅ PING OK"
fi
echo

echo "2. 🛣️ Verificando rota para $SERVER_IP..."
ip route get $SERVER_IP 2>/dev/null || echo "❌ Rota não encontrada"
echo

echo "3. 🔌 Interfaces de rede locais:"
ip addr show | grep -E "(inet |UP,)"
echo

echo "4. 🔍 Verificando se a porta está aberta no servidor..."
timeout 5 nc -zv $SERVER_IP $SERVER_PORT 2>&1
NC_RESULT=$?
echo

echo "5. 📡 Testando UDP com netcat (timeout 10s)..."
echo "NETCAT_TEST_$(date +%s)" | timeout 10 nc -u -w 5 $SERVER_IP $SERVER_PORT
echo "Status netcat: $?"
echo

echo "6. 🏥 Verificações do sistema local:"
echo "   - Processos usando a porta $SERVER_PORT:"
ss -ulnp | grep ":$SERVER_PORT " || echo "     Nenhum processo local usando a porta"
echo "   - Regras de firewall (iptables):"
sudo iptables -L | grep -i "$SERVER_PORT" || echo "     Nenhuma regra específica encontrada"
echo

echo "7. 🧪 Teste com cliente customizado (1 iteração)..."
if [ -f "./client_udp" ]; then
    echo "Executando: timeout 15 ./client_udp auto $SERVER_IP $SERVER_PORT 1"
    timeout 15 ./client_udp auto $SERVER_IP $SERVER_PORT 1
    CLIENT_RESULT=$?
    echo "Status cliente: $CLIENT_RESULT"
else
    echo "❌ Arquivo client_udp não encontrado - compile primeiro"
fi
echo

echo "8. 🖥️ Informações do WSL (se aplicável):"
if grep -qi microsoft /proc/version 2>/dev/null; then
    echo "   - Detectado ambiente WSL"
    echo "   - IP WSL: $(hostname -I | awk '{print $1}')"
    echo "   - Para acesso externo, configure port forwarding:"
    echo "     netsh interface portproxy add v4tov4 listenport=$SERVER_PORT listenaddress=0.0.0.0 connectport=$SERVER_PORT connectaddress=$(hostname -I | awk '{print $1}')"
fi
echo

echo "=== 📋 RESUMO DO DIAGNÓSTICO ==="
if [ $PING_RESULT -eq 0 ]; then
    echo "✅ Conectividade de rede: OK"
else
    echo "❌ Conectividade de rede: FALHA"
fi

if [ $NC_RESULT -eq 0 ]; then
    echo "✅ Porta TCP accessível: OK"
else
    echo "⚠️ Porta TCP: Não acessível (normal para UDP)"
fi

echo
echo "🔧 PRÓXIMOS PASSOS RECOMENDADOS:"
echo "1. Verifique se o servidor está rodando: ps aux | grep server_udp"
echo "2. No servidor, execute: ss -ulnp | grep $SERVER_PORT"
echo "3. Se WSL, configure port forwarding no Windows"
echo "4. Teste firewall: sudo ufw status (Ubuntu) ou iptables -L"
echo "5. Execute o servidor com logs: ./server_udp 0.0.0.0 $SERVER_PORT"
echo
echo "=== Fim do diagnóstico ==="
