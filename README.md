# Avaliação de Desempenho de Rede UDP

Este projeto mede o RTT (Round-Trip Time) de pacotes UDP em dois experimentos:

1. **Experimento 1**: RTT vs tamanho de payload (taxa constante)  
2. **Experimento 2**: RTT vs taxa de requisições (geração de rampa)

Ambos os experimentos são executados em redes simuladas de 10 Mb/s e 100 Mb/s com um servidor UDP iterativo que ecoa cada datagrama recebido.

---

## 1. Clonando o Repositório

```bash
git clone https://github.com/mzet97/Trabalho_Sistemas_Distribuidos_Aspectos_Praticos.git
cd Trabalho_Sistemas_Distribuidos_Aspectos_Praticos
```

---

## 2. Estrutura do Projeto

### Estrutura de Diretórios

```text
.
├── client1/              # Diretório para dados do Cliente 1 (gerado dinamicamente)
├── client2/              # Diretório para dados do Cliente 2 (gerado dinamicamente)  
├── server/               # Diretório para configurações do servidor
├── graficos/             # Diretório para gráficos gerados (criado automaticamente)
├── .vscode/              # Configurações do VS Code
│   └── settings.json     # Associações de arquivos
├── .gitignore            # Arquivos ignorados pelo Git
├── LICENSE               # Licença MIT
└── README.md             # Este arquivo
```

### Arquivos Fonte

```text
server_udp.c              # Servidor UDP echo
client_udp.c              # Cliente para Experimento 1
client_udp_ramp.c         # Cliente para Experimento 2
Makefile                  # Script de compilação
analyze.py                # Análise estatística avançada (Python)
plot.py                   # Geração de gráficos interpretativos (Python)
plot_commands.gnuplot     # Comandos para gerar gráficos (Gnuplot - opcional)
analyze_packets.sh        # Análise de captura de pacotes com tcpdump
```

### Scripts de Execução Automatizada

#### Experimento 1 (RTT vs Tamanho) - 1000 execuções

```text
run_client1_10.sh         # Cliente 1 - Rede 10 Mbps
run_client1_100.sh        # Cliente 1 - Rede 100 Mbps
run_client2_10.sh         # Cliente 2 - Rede 10 Mbps
run_client2_100.sh        # Cliente 2 - Rede 100 Mbps
```

#### Experimento 2 (RTT vs Taxa Rampa) - 100 execuções

```text
run_client1_ramp_10.sh    # Cliente 1 Rampa - Rede 10 Mbps
run_client1_ramp_100.sh   # Cliente 1 Rampa - Rede 100 Mbps
run_client2_ramp_10.sh    # Cliente 2 Rampa - Rede 10 Mbps
run_client2_ramp_100.sh   # Cliente 2 Rampa - Rede 100 Mbps
```

### Arquivos Gerados Após Execução

#### Dados Brutos

```text
raw_data_cliente1.csv       # Medições brutas - Cliente 1 (Exp. 1 - 10 Mbps)
raw_data_cliente1_100.csv   # Medições brutas - Cliente 1 (Exp. 1 - 100 Mbps)
raw_data_cliente2.csv       # Medições brutas - Cliente 2 (Exp. 1 - 10 Mbps)
raw_data_cliente2_100.csv   # Medições brutas - Cliente 2 (Exp. 1 - 100 Mbps)
ramp_data_cliente1.csv      # Medições de rampa - Cliente 1 (Exp. 2 - 10 Mbps)
ramp_data_cliente1_100.csv  # Medições de rampa - Cliente 1 (Exp. 2 - 100 Mbps)
ramp_data_cliente2.csv      # Medições de rampa - Cliente 2 (Exp. 2 - 10 Mbps)
ramp_data_cliente2_100.csv  # Medições de rampa - Cliente 2 (Exp. 2 - 100 Mbps)
```

#### Estatísticas Processadas

```text
stats_cliente1.csv          # Estatísticas detalhadas - Cliente 1 (10 Mbps)
stats_cliente1_100.csv      # Estatísticas detalhadas - Cliente 1 (100 Mbps)
stats_cliente2.csv          # Estatísticas detalhadas - Cliente 2 (10 Mbps)
stats_cliente2_100.csv      # Estatísticas detalhadas - Cliente 2 (100 Mbps)
stats_ramp_cliente1.csv     # Estatísticas por nível - Cliente 1 (10 Mbps)
stats_ramp_cliente1_100.csv # Estatísticas por nível - Cliente 1 (100 Mbps)
stats_ramp_cliente2.csv     # Estatísticas por nível - Cliente 2 (10 Mbps)
stats_ramp_cliente2_100.csv # Estatísticas por nível - Cliente 2 (100 Mbps)
stats_network_10mbps.csv    # Estatísticas agregadas - Rede 10 Mbps
stats_network_100mbps.csv   # Estatísticas agregadas - Rede 100 Mbps
```

#### Gráficos Gerados (Python - Recomendado)

```text
graficos/01_rtt_cliente1_10mbps.png        # RTT Cliente 1 - 10 Mbps (simplificado)
graficos/02_rtt_cliente1_100mbps.png       # RTT Cliente 1 - 100 Mbps (simplificado)
graficos/03_comparacao_rtt_redes.png       # Comparação RTT entre redes
graficos/04_comparacao_perda_redes.png     # Comparação taxa de perda
graficos/05_comparacao_jitter_redes.png    # Comparação jitter médio
graficos/06_comparacao_percentis.png       # Comparação P95 e P99
graficos/07_dashboard_rede_comparativo.png # Dashboard completo 2x2
graficos/08_cliente1_comparacao_rede.png   # Cliente 1 com intervalos de confiança
graficos/09_cliente2_comparacao_rede.png   # Cliente 2 com intervalos de confiança
graficos/10_ramp_cliente1_rtt_carga.png    # Análise de rampa RTT vs carga
graficos/11_ramp_perda_vs_nivel.png        # Taxa de perda vs nível de rampa
graficos/12_analise_saturacao.png          # RTT normalizado (análise saturação)
```

#### Gráficos Alternativos (Gnuplot - Opcional)

```text
rtt_cliente1_10mbps.png                     # RTT com IC 98% e percentis - Cliente 1
rtt_cliente1_100mbps.png                    # RTT com IC 98% e percentis - Cliente 1 (100 Mbps)
network_comparison_rtt.png                  # Comparação RTT entre redes
network_comparison_loss.png                 # Taxa de perda vs tamanho
network_comparison_jitter.png               # Jitter vs tamanho
network_comparison_percentiles.png          # Comparação P95/P99
network_dashboard.png                       # Dashboard 3x2 completo
cliente1_network_comparison.png             # Cliente 1 comparação redes
cliente2_network_comparison.png             # Cliente 2 comparação redes
ramp_cliente1_network_comparison.png        # Rampa Cliente 1
ramp_loss_network_comparison.png            # Taxa de perda na rampa
saturation_analysis.png                     # Análise de saturação
```

#### Logs de Análise de Rede

```text
tcpdump_raw_[timestamp].log         # Captura bruta de pacotes
tcpdump_analysis_[timestamp].log    # Análise detalhada da captura
tcpdump_capture_[timestamp].pcap    # Arquivo PCAP para Wireshark
```

---

## 3. Pré-requisitos

1. **Sistema Operacional**  
   Windows 10/11 com WSL (Ubuntu) instalado, ou Linux nativo.

2. **Pacotes necessários no Ubuntu/WSL**  

   ```bash
   sudo apt update
   sudo apt install -y build-essential iproute2 python3 python3-pip python3-pandas python3-matplotlib python3-numpy tcpdump bc gnuplot-nox
   ```

   - `build-essential`: GCC, make e bibliotecas padrão  
   - `iproute2`: utilitário `tc` para simular limitação de banda  
   - `python3`: necessário para análise e gráficos
   - `python3-pandas`: manipulação de dados
   - `python3-matplotlib`: geração de gráficos
   - `python3-numpy`: computação numérica
   - `tcpdump`: captura e análise de pacotes de rede
   - `bc`: calculadora para scripts bash
   - `gnuplot-nox`: Gnuplot (opcional, para gráficos alternativos)

---

## 4. Compilação

No diretório do projeto, execute:

```bash
make all
```

Isso vai gerar os seguintes executáveis:

- `server_udp` → servidor UDP iterativo  
- `client_udp` → cliente para Experimento 1 (RTT × tamanho)  
- `client_udp_ramp` → cliente para Experimento 2 (RTT × taxa de rampa)

Para remover somente os executáveis:

```bash
make clean
```

Para remover executáveis e todos os dados gerados (CSVs e PNGs):

```bash
make distclean
```

---

## 5. Configuração de Rede (Simulação de Banda)

### 5.1 Verificando Interfaces Disponíveis

```bash
ip addr show
```

### 5.2 Configurando Limitação de Banda (opcional)

Para simular redes de 10 Mbps e 100 Mbps usando `tc`:

```bash
# Interface 1 - 10 Mbps
sudo tc qdisc add dev eth0 root tbf rate 10mbit burst 32kbit latency 40ms

# Interface 2 - 100 Mbps  
sudo tc qdisc add dev eth1 root tbf rate 100mbit burst 32kbit latency 40ms
```

Para remover as limitações:

```bash
sudo tc qdisc del dev eth0 root
sudo tc qdisc del dev eth1 root
```

---

## 6. Executando o Servidor

Abra duas abas/janelas no terminal:

1. **Aba 1 (rede 10 Mb/s)**  

   ```bash
   ./server_udp 10.0.0.12 50000
   ```

2. **Aba 2 (rede 100 Mb/s)**  

   ```bash
   ./server_udp 100.0.012 50000
   ```

O servidor imprime estatísticas básicas e pode ser interrompido com Ctrl+C.

---

## 7. Experimento 1: RTT vs Tamanho de Payload

### 7.1 Execução Automatizada por Rede

#### Rede 10 Mbps (1000 execuções por cliente)

```bash
chmod +x run_client1_10.sh run_client2_10.sh

# Em terminais separados
./run_client1_10.sh &
./run_client2_10.sh &
```

#### Rede 100 Mbps (1000 execuções por cliente)

```bash
chmod +x run_client1_100.sh run_client2_100.sh

# Em terminais separados  
./run_client1_100.sh &
./run_client2_100.sh &
```

### 7.2 Execução Manual

Para executar apenas uma vez:

```bash
# Cliente 1 (10 Mbps)
./client_udp auto 10.0.0.12 9090 1

# Cliente 2 (100 Mbps)
./client_udp auto 100.0.0.12 9090 2
```

### 7.3 Parâmetros do Experimento

- **Tamanhos testados**: 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65507 bytes
- **Medições por tamanho**: 1000
- **Timeout**: 10 segundos

---

## 8. Experimento 2: RTT vs Taxa de Requisições (Rampa)

### 8.1 Descrição da Rampa

- **Taxa mínima**: 10 req/s (nível 1)
- **Taxa máxima**: 100 req/s (nível 10)  
- **Níveis**: 19 total (10 subida + 9 descida)
- **Requisições por nível**: 100

### 8.2 Execução Automatizada por Rede

#### Rede 10 Mbps (100 execuções por cliente)

```bash
chmod +x run_client1_ramp_10.sh run_client2_ramp_10.sh

# Em terminais separados
./run_client1_ramp_10.sh &
./run_client2_ramp_10.sh &
```

#### Rede 100 Mbps (100 execuções por cliente)

```bash
chmod +x run_client1_ramp_100.sh run_client2_ramp_100.sh

# Em terminais separados
./run_client1_ramp_100.sh &
./run_client2_ramp_100.sh &
```

### 8.3 Execução Manual

```bash
# Cliente 1 (10 Mbps)
./client_udp_ramp auto 10.0.0.12 9090 1

# Cliente 2 (100 Mbps)
./client_udp_ramp auto 100.0.0.12 9090 2
```

---

## 9. Análise Estatística Avançada

### 9.1 Processamento dos Dados

Após completar os experimentos:

```bash
python3 analyze.py
```

### 9.2 Estatísticas Calculadas

O script `analyze.py` calcula:

- **Medidas básicas**: média, mediana, desvio padrão
- **Intervalo de confiança**: 98% (Z = 2.3263)
- **Percentis**: P95 e P99
- **Jitter**: variação média entre RTTs consecutivos
- **Taxa de perda**: porcentagem de timeouts
- **Detecção de outliers**: método IQR
- **Nível de saturação**: ponto onde RTT aumenta >50%
- **Agregação por rede**: estatísticas combinadas de ambos os clientes

### 9.3 Arquivos de Saída

#### Para Experimento 1

- `stats_cliente[1-2].csv`: 14 colunas com estatísticas completas por cliente
- `stats_cliente[1-2]_100.csv`: estatísticas para rede 100 Mbps
- `stats_network_[10|100]mbps.csv`: estatísticas agregadas por rede

#### Para Experimento 2

- `stats_ramp_cliente[1-2].csv`: estatísticas por (tamanho, nível) - 10 Mbps
- `stats_ramp_cliente[1-2]_100.csv`: estatísticas por (tamanho, nível) - 100 Mbps

### 9.4 Relatório Resumido

O script gera automaticamente um relatório no terminal com:

- RTT mínimo/máximo global por rede
- Taxa de perda média e máxima
- Tamanho com maior perda de pacotes
- Análise comparativa entre redes
- Estatísticas de registros válidos vs timeouts

---

## 10. Geração de Gráficos

### 10.1 Gráficos Interpretativos com Python (Recomendado)

```bash
python3 plot.py
```

**Características dos gráficos Python:**

- **Subamostragem inteligente**: reduz pontos mantendo distribuição logarítmica
- **Cores contrastantes**: esquema de cores com alto contraste visual
- **Formatação legível**: eixos formatados em KB/MB, títulos claros
- **Visualização simplificada**: foco nas tendências principais
- **Dashboard resumido**: métricas principais em layout 2x2

**Gráficos gerados (12 arquivos PNG):**

1. RTT vs Tamanho - Cliente 1 (10 Mbps) - simplificado
2. RTT vs Tamanho - Cliente 1 (100 Mbps) - simplificado  
3. Comparação direta RTT (10 vs 100 Mbps) - versão limpa
4. Comparação Taxa de Perda (com cores contrastantes)
5. Comparação Jitter Médio (rosa vs verde)
6. Comparação Percentis P95/P99 (laranja vs azul)
7. Dashboard Resumido 2x2 (RTT, Perda, Jitter, Speedup)
8. Cliente 1 - Comparação entre Redes (com IC 98%)
9. Cliente 2 - Comparação entre Redes (roxo vs amarelo)
10. Rampa RTT vs Nível de Carga (1KB)
11. Taxa de Perda vs Nível de Rampa (1KB e 64KB)
12. Análise de Saturação - RTT Normalizado

### 10.2 Gráficos Detalhados com Gnuplot (Opcional)

```bash
gnuplot plot_commands.gnuplot
```

**Características dos gráficos Gnuplot:**

- **Todos os pontos**: sem subamostragem, dados completos
- **Múltiplas métricas**: IC 98%, percentis, outliers
- **Dashboard 3x2**: layout mais denso
- **Análise avançada**: speedup, saturação, normalização

Gera 12+ gráficos incluindo análises detalhadas de percentis, jitter e saturação.

### 10.3 Comparação dos Métodos

| Aspecto | Python (plot.py) | Gnuplot (plot_commands.gnuplot) |
|---------|------------------|----------------------------------|
| **Interpretabilidade** | ★★★★★ Excelente | ★★★☆☆ Boa |
| **Velocidade** | ★★★★☆ Rápida | ★★☆☆☆ Lenta |
| **Personalização** | ★★★★★ Flexível | ★★★☆☆ Limitada |
| **Dependências** | Python padrão | Gnuplot + AWK |
| **Tamanho arquivos** | Menor (subamostragem) | Maior (todos os pontos) |
| **Recomendação** | **Uso geral** | Análise científica detalhada |

---

## 11. Interpretação dos Resultados

### 11.1 Experimento 1 - RTT vs Tamanho

**O que observar:**

- Crescimento do RTT com tamanho do payload
- Diferença entre redes 10 Mbps e 100 Mbps
- Impacto da fragmentação (>1500 bytes)
- Variabilidade (jitter) em diferentes tamanhos

**Métricas importantes:**

- RTT médio e mediana (robustez a outliers)
- P95/P99 (cauda de latência)
- Taxa de perda (confiabilidade)
- Speedup (RTT_10Mbps / RTT_100Mbps)

### 11.2 Experimento 2 - RTT vs Taxa

**O que observar:**

- Ponto de saturação da rede
- Degradação do RTT com aumento da taxa
- Diferença de capacidade entre 10/100 Mbps
- Comportamento na subida vs descida da rampa

**Análise de saturação:**

- Nível onde RTT aumenta >50% do baseline
- Taxa correspondente em req/s
- Comparação entre tamanhos de payload
- RTT normalizado para identificar saturação

### 11.3 Insights dos Gráficos

**Dashboard Resumido:**

- **RTT Médio**: tendência geral de latência
- **Taxa de Perda**: confiabilidade da rede
- **Jitter**: estabilidade da rede
- **Speedup**: benefício da rede mais rápida

**Análise de Saturação:**

- **Limiar 150%**: ponto crítico de degradação
- **Normalização**: comparação justa entre cenários
- **Diferentes tamanhos**: impacto do payload na saturação

---

## 12. Solução de Problemas

### 12.1 Timeouts Excessivos

```bash
# Verificar conectividade
ping -c 5 10.0.0.12
ping -c 5 100.0.012

# Testar servidor manualmente
echo "TEST" | nc -u 10.0.0.12 50000
```

### 12.2 Erro de Bind

- Verificar se IPs estão corretos: `ip addr show`
- Usar `auto` para bind automático
- Verificar permissões (pode precisar sudo)

### 12.3 Arquivos CSV Vazios

- Verificar se servidor está rodando
- Conferir logs de erro dos clientes
- Validar parâmetros de linha de comando

### 12.4 Problemas com Gráficos Python

```bash
# Instalar dependências se necessário
pip3 install pandas matplotlib numpy

# Verificar versão Python
python3 --version  # Deve ser >= 3.6

# Teste básico
python3 -c "import pandas, matplotlib, numpy; print('OK')"
```

### 12.5 Problemas com Gnuplot

```bash
# Verificar instalação
gnuplot --version

# Teste básico
echo "plot sin(x)" | gnuplot

# Verificar arquivos CSV
head -5 stats_cliente1.csv
```

---

## 13. Estrutura dos CSVs

### 13.1 raw_data_cliente[1-2][ _100].csv

```csv
tamanho_bytes,iteracao,rtt_ms
2,1,0.12345
2,2,-1.00000  # timeout
...
```

### 13.2 stats_cliente[1-2][_100].csv

```csv
tamanho_bytes,n_validos,media_ms,mediana_ms,dp_ms,jitter_ms,ic_lower_ms,ic_upper_ms,p95_ms,p99_ms,min_ms,max_ms,taxa_perda_%,num_outliers
2,995,0.15234,0.14523,0.02341,0.01234,0.14123,0.16345,0.19234,0.21345,0.10234,0.25432,0.50,3
...
```

### 13.3 stats_network_[10|100]mbps.csv

```csv
tamanho_bytes,media_agregada_ms,mediana_agregada_ms,p95_agregado_ms,p99_agregado_ms,jitter_agregado_ms,taxa_perda_agregada_%,n_total_amostras
2,0.15234,0.14523,0.19234,0.21345,0.01234,0.50,1990
...
```

### 13.4 stats_ramp_cliente[1-2][ _100].csv

```csv
tamanho_bytes,nivel,n_validos,media_ms,mediana_ms,dp_ms,jitter_ms,ic_lower_ms,ic_upper_ms,p95_ms,p99_ms,min_ms,max_ms,taxa_perda_%,num_outliers
2,1,98,0.25432,0.23421,0.05432,0.03421,0.24123,0.26741,0.35432,0.42345,0.15432,0.52341,2.00,1
...
```

---

## 14. Fluxo de Trabalho Recomendado

1. **Preparação**

   ```bash
   make all
   # Iniciar servidores em terminais separados
   ```

2. **Coleta de Dados**

   ```bash
   # Executar experimentos (pode levar horas)
   ./run_client1_10.sh &
   ./run_client1_100.sh &
   # ... outros scripts
   ```

3. **Análise Estatística**

   ```bash
   python3 analyze.py
   ```

4. **Geração de Gráficos**

   ```bash
   python3 plot.py  # Recomendado para relatórios
   # ou
   gnuplot plot_commands.gnuplot  # Para análise científica
   ```

5. **Visualização**

   ```bash
   ls graficos/  # Ver gráficos gerados
   ```

---

## 15. Considerações de Performance

- **Tempo de execução**: Experimento completo ~6-8 horas
- **Espaço em disco**: ~50-100 MB de dados + ~10-20 MB de gráficos
- **Memória**: Análise Python requer ~200-500 MB RAM
- **CPU**: Múltiplos clientes podem saturar CPU em máquinas lentas

---

## 16. Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.
