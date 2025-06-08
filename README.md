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

## 2. Estrutura de Arquivos

### Arquivos Fonte

```
server_udp.c              # Servidor UDP echo
client_udp.c              # Cliente para Experimento 1
client_udp_ramp.c         # Cliente para Experimento 2
Makefile                  # Script de compilação
analyze.py                # Análise estatística avançada
plot_commands.gnuplot     # Comandos para gerar gráficos básicos
plot_commands_improved.gnuplot  # Comandos para gráficos detalhados
run_30_cycles.sh          # Executa 30 ciclos do Experimento 1
run_client1.sh            # Executa Cliente 1 em loop
run_client2.sh            # Executa Cliente 2 em loop
README.md                 # Este arquivo
```

### Arquivos Gerados Após Execução

#### Dados Brutos

```
raw_data_cliente1.csv       # Medições brutas - Cliente 1 (Exp. 1)
raw_data_cliente2.csv       # Medições brutas - Cliente 2 (Exp. 1)
ramp_data_cliente1.csv      # Medições de rampa - Cliente 1 (Exp. 2)
ramp_data_cliente2.csv      # Medições de rampa - Cliente 2 (Exp. 2)
```

#### Estatísticas Processadas

```
stats_cliente1.csv          # Estatísticas detalhadas - Cliente 1 (Exp. 1)
stats_cliente2.csv          # Estatísticas detalhadas - Cliente 2 (Exp. 1)
stats_ramp_cliente1.csv     # Estatísticas por nível - Cliente 1 (Exp. 2)
stats_ramp_cliente2.csv     # Estatísticas por nível - Cliente 2 (Exp. 2)
stats_ramp_aggregated_cliente1.csv  # Estatísticas agregadas - Cliente 1
stats_ramp_aggregated_cliente2.csv  # Estatísticas agregadas - Cliente 2
```

#### Gráficos Gerados

```
# Gráficos básicos
rtt_vs_size_cliente1.png    # RTT vs tamanho - Cliente 1
rtt_vs_size_cliente2.png    # RTT vs tamanho - Cliente 2
rtt_ramp_vs_level_cliente1.png  # RTT vs nível rampa - Cliente 1
rtt_ramp_vs_level_cliente2.png  # RTT vs nível rampa - Cliente 2

# Gráficos detalhados (com analyze.py melhorado)
rtt_vs_size_cliente1_detailed.png   # RTT com IC 98% e percentis
rtt_vs_size_cliente2_detailed.png   # RTT com IC 98% e percentis
loss_rate_vs_size.png               # Taxa de perda vs tamanho
jitter_vs_size.png                  # Jitter vs tamanho
rtt_ramp_vs_level_cliente1_detailed.png  # Rampa com percentis
rtt_ramp_vs_level_cliente2_detailed.png  # Rampa com percentis
loss_rate_ramp.png                  # Taxa de perda na rampa
percentiles_comparison.png          # Comparação P95/P99
outliers_histogram.png              # Histograma de outliers
```

---

## 3. Pré-requisitos

1. **Sistema Operacional**  
   Windows 10/11 com WSL (Ubuntu) instalado, ou Linux nativo.

2. **Pacotes necessários no Ubuntu/WSL**  

   ```bash
   sudo apt update
   sudo apt install -y build-essential iproute2 gnuplot-nox python3 python3-pip
   ```

   - `build-essential`: GCC, make e bibliotecas padrão  
   - `iproute2`: utilitário `tc` para simular limitação de banda  
   - `gnuplot-nox`: Gnuplot em modo texto (gera PNG sem interface gráfica)  
   - `python3`: necessário para o script `analyze.py`

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
   ./server_udp 10.0.10.12 50000
   ```

2. **Aba 2 (rede 100 Mb/s)**  

   ```bash
   ./server_udp 10.0.100.12 50000
   ```

O servidor imprime estatísticas básicas e pode ser interrompido com Ctrl+C.

---

## 7. Experimento 1: RTT vs Tamanho de Payload

### 7.1 Execução Automatizada (30 ciclos)

```bash
chmod +x run_30_cycles.sh
./run_30_cycles.sh
```

Este script executa 30 ciclos completos com ambos os clientes em paralelo.

### 7.2 Execução Manual

Para executar apenas uma vez:

```bash
# Cliente 1 (10 Mbps)
./client_udp 10.0.10.11 10.0.10.12 50000 1

# Cliente 2 (100 Mbps)
./client_udp 10.0.100.11 10.0.100.12 50000 2
```

### 7.3 Parâmetros do Experimento

- **Tamanhos testados**: 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65507 bytes
- **Medições por tamanho**: 1000
- **Warmup**: 50 pacotes
- **Timeout**: 10 segundos

---

## 8. Experimento 2: RTT vs Taxa de Requisições (Rampa)

### 8.1 Descrição da Rampa

- **Taxa mínima**: 10 req/s (nível 1)
- **Taxa máxima**: 100 req/s (nível 10)  
- **Níveis**: 19 total (10 subida + 9 descida)
- **Requisições por nível**: 100

### 8.2 Execução

```bash
# Cliente 1 (10 Mbps)
./client_udp_ramp 10.0.10.11 10.0.10.12 50000 1

# Cliente 2 (100 Mbps)
./client_udp_ramp 10.0.100.11 10.0.100.12 50000 2
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

### 9.3 Arquivos de Saída

#### Para Experimento 1

- `stats_cliente[1-2].csv`: 14 colunas com estatísticas completas

#### Para Experimento 2

- `stats_ramp_cliente[1-2].csv`: estatísticas por (tamanho, nível)
- `stats_ramp_aggregated_cliente[1-2].csv`: agregado por tamanho

### 9.4 Relatório Resumido

O script gera automaticamente um relatório no terminal com:

- RTT mínimo/máximo global
- Taxa de perda média
- Tamanho com maior variabilidade
- Níveis de saturação detectados
- Estatísticas de percentis

---

## 10. Geração de Gráficos

### 10.1 Gráficos Básicos

```bash
gnuplot plot_commands.gnuplot
```

Gera 4 gráficos básicos com média e desvio padrão.

### 10.2 Gráficos Detalhados

```bash
gnuplot plot_commands_improved.gnuplot
```

Gera 8+ gráficos incluindo:

- RTT com intervalo de confiança 98%
- Percentis P95 e P99
- Taxa de perda vs tamanho
- Jitter vs tamanho
- Comparações entre clientes
- Análise de saturação na rampa

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

---

## 12. Solução de Problemas

### 12.1 Timeouts Excessivos

```bash
# Verificar conectividade
ping -c 5 10.0.10.12
ping -c 5 10.0.100.12

# Testar servidor manualmente
echo "TEST" | nc -u 10.0.10.12 50000
```

### 12.2 Erro de Bind

- Verificar se IPs estão corretos: `ip addr show`
- Usar `auto` para bind automático
- Verificar permissões (pode precisar sudo)

### 12.3 Arquivos CSV Vazios

- Verificar se servidor está rodando
- Conferir logs de erro dos clientes
- Validar parâmetros de linha de comando

---

## 13. Estrutura dos CSVs

### 13.1 raw_data_cliente[1-2].csv

```csv
tamanho_bytes,iteracao,rtt_ms
2,1,0.12345
2,2,-1.00000  # timeout
...
```

### 13.2 stats_cliente[1-2].csv

```csv
tamanho_bytes,n_validos,media_ms,mediana_ms,dp_ms,jitter_ms,ic_lower_ms,ic_upper_ms,p95_ms,p99_ms,min_ms,max_ms,taxa_perda_%,num_outliers
2,995,0.15234,0.14523,0.02341,0.01234,0.14123,0.16345,0.19234,0.21345,0.10234,0.25432,0.50,3
...
```

### 13.3 stats_ramp_aggregated_cliente[1-2].csv

```csv
tamanho_bytes,n_total,media_ms,mediana_ms,dp_ms,jitter_ms,p95_ms,p99_ms,min_ms,max_ms,taxa_perda_%,nivel_saturacao
2,1850,0.25432,0.23421,0.05432,0.03421,0.35432,0.42345,0.15432,0.52341,7.89,15
...
```

---
