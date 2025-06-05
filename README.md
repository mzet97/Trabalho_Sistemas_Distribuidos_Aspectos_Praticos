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

Na raiz do repositório, você deve encontrar:

```
server_udp.c
client_udp.c
client_udp_ramp.c
Makefile
analyze.py
plot_commands.gnuplot
run_30_cycles.sh
run_client1.sh
run_client2.sh
README.md  (este arquivo)
```

Após compilação e execução, serão gerados (na raiz):

```
server_udp                  (executável do servidor)
client_udp                  (executável do cliente – Exp. 1)
client_udp_ramp             (executável do cliente – Exp. 2)
raw_data_cliente1.csv       (dados brutos – Exp. 1, Cliente 1)
raw_data_cliente2.csv       (dados brutos – Exp. 1, Cliente 2)
ramp_data_cliente1.csv      (dados de rampa – Exp. 2, Cliente 1)
ramp_data_cliente2.csv      (dados de rampa – Exp. 2, Cliente 2)
stats_cliente1.csv          (estatísticas do Exp. 1, Cliente 1)
stats_cliente2.csv          (estatísticas do Exp. 1, Cliente 2)
stats_ramp_cliente1.csv     (estatísticas do Exp. 2, Cliente 1)
stats_ramp_cliente2.csv     (estatísticas do Exp. 2, Cliente 2)
rtt_vs_size_cliente1.png    (gráfico RTT vs tamanho – Cliente 1)
rtt_vs_size_cliente2.png    (gráfico RTT vs tamanho – Cliente 2)
rtt_ramp_vs_level_cliente1.png  (gráfico RTT vs nível de rampa – Cliente 1)
rtt_ramp_vs_level_cliente2.png  (gráfico RTT vs nível de rampa – Cliente 2)
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

Ou, para compilar individualmente:

```bash
make server_udp
make client_udp
make client_udp_ramp
```

Para remover somente os executáveis:

```bash
make clean
```

Para remover executáveis e todos os dados gerados (CSVs e PNGs):

```bash
make distclean
```

---

## 6. Executando o Servidor

Abra duas abas/janelas no Ubuntu/WSL:

1. **Aba 1 (rede 10 Mb/s / eth1)**  

   ```bash
   ./server_udp 10.0.10.12 50000
   ```

   - Faz bind em `10.0.10.12:50000`.

2. **Aba 2 (rede 100 Mb/s / eth2)**  

   ```bash
   ./server_udp 10.0.100.12 50000
   ```

   - Faz bind em `10.0.100.12:50000`.

Cada instância do servidor executa:

```c
while (1) {
    recvfrom(...);
    sendto(...);
}
```

---

## 7. Experimento 1: RTT vs Tamanho de Payload

### 7.1 Uso do Script de 30 Ciclos

Na raiz do projeto, torne executável:

```bash
chmod +x run_30_cycles.sh
```

Em seguida, execute:

```bash
./run_30_cycles.sh
```

Esse script repete 30 ciclos de:

1. **Cliente 1** (bind local em `10.0.10.11`, envia para `10.0.10.12:50000`) em background  
2. **Cliente 2** (bind local em `10.0.100.11`, envia para `10.0.100.12:50000`) em background  
3. `wait` para aguardar ambos terminarem, e então inicia o próximo ciclo

Após cada execução, os clientes gravam/concatenam em:

- `raw_data_cliente1.csv`  
- `raw_data_cliente2.csv`

Cada arquivo terá, ao final, aproximadamente:  

```
30 ciclos × 16 tamanhos × 1000 medidas ≃ 480000 linhas + cabeçalho
```

### 7.2 Execução Alternativa em Parâmetros

Para rodar apenas o Cliente 1 ou apenas o Cliente 2 simultaneamente:

```bash
chmod +x run_client1.sh run_client2.sh

# Em um terminal:
./run_client1.sh   # 30 instâncias do Cliente 1 em background

# Em outro terminal:
./run_client2.sh   # 30 instâncias do Cliente 2 em background
```

---

## 8. Experimento 2: RTT vs Taxa de Requisições (Rampa)

### 8.1 Descrição do Experimento

O cliente de rampa (`client_udp_ramp.c`) varia a taxa de envio de requisições conforme:

- **Taxa mínima (nível 1)**: 10 req/s → intervalo = 100000 µs  
- **Taxa máxima (nível 10)**: 100 req/s → intervalo = 10000 µs  
- **Níveis totais**: 10 na subida + 9 na descida = 19 níveis  
- **Requisições por nível**: 100

Para cada tamanho de payload, o cliente:

1. Começa em 10 req/s e envia 100 pacotes;  
2. Aumenta a taxa até 100 req/s em 10 passos, enviando 100 pacotes em cada passo;  
3. Então diminui de volta a 10 req/s em 9 passos, 100 pacotes por passo;  
4. Registra o RTT de cada pacote em CSV.

### 8.2 Executando o Cliente de Rampa

Em terminais separados:

```bash
# Cliente 1 (rede 10 Mb/s):
./client_udp_ramp 10.0.10.11 10.0.10.12 50000 1

# Cliente 2 (rede 100 Mb/s):
./client_udp_ramp 10.0.100.11 10.0.100.12 50000 2
```

Os dados serão gravados (append) em:

- `ramp_data_cliente1.csv`  
- `ramp_data_cliente2.csv`

Formato de cada linha:

```
tamanho_bytes,nivel,iteracao_no_nivel,rtt_ms
```

---

## 9. Processando Dados Brutos em Estatísticas

Após completar os experimentos e preencher todos os arquivos:

- `raw_data_cliente1.csv`  
- `raw_data_cliente2.csv`  
- `ramp_data_cliente1.csv`  
- `ramp_data_cliente2.csv`

execute:

```bash
python3 analyze.py
```

Isso gerará, na raiz:

```
stats_cliente1.csv         (dados do Exp. 1)
stats_cliente2.csv
stats_ramp_cliente1.csv    (dados do Exp. 2)
stats_ramp_cliente2.csv
```

### 9.1 Formato de `stats_clienteX.csv`

```
tamanho_bytes,n_validos,media_ms,mediana_ms,dp_ms,jitter_ms,ic_lower_ms,ic_upper_ms
```

- Agrupado somente por `tamanho_bytes`.

### 9.2 Formato de `stats_ramp_clienteX.csv`

```
tamanho_bytes,nivel,n_validos,media_ms,mediana_ms,dp_ms,jitter_ms,ic_lower_ms,ic_upper_ms
```

- Agrupado por `(tamanho_bytes, nivel)`.

---

## 10. Gerando Gráficos com Gnuplot

Certifique-se de que `plot_commands.gnuplot` contenha:

```gnuplot
set datafile separator ","
set terminal pngcairo size 1024,768 enhanced font "Arial,10"
set grid

set output "rtt_vs_size_cliente1.png"
set title "RTT Médio vs Tamanho de Payload — Cliente 1"
set xlabel "Tamanho do Payload (bytes)"
set ylabel "RTT (ms)"
plot   "stats_cliente1.csv" skip 1 using 1:3 with linespoints lt rgb "blue"  lw 2 pt 7 title "Média",   ""                     skip 1 using 1:3:5 with yerrorbars lt rgb "red"   lw 1 title "Desvio Padrão"

set output "rtt_vs_size_cliente2.png"
set title "RTT Médio vs Tamanho de Payload — Cliente 2"
set xlabel "Tamanho do Payload (bytes)"
set ylabel "RTT (ms)"
plot   "stats_cliente2.csv" skip 1 using 1:3 with linespoints lt rgb "green"  lw 2 pt 7 title "Média",   ""                     skip 1 using 1:3:5 with yerrorbars lt rgb "magenta" lw 1 title "Desvio Padrão"

set output "rtt_ramp_vs_level_cliente1.png"
set title "RTT Médio vs Nível (Rampa) — Cliente 1"
set xlabel "Nível da Rampa"
set ylabel "RTT (ms)"
plot   "stats_ramp_cliente1.csv" skip 1 using 2:4 with linespoints lt rgb "blue"  lw 2 pt 7 title "Média",   ""                         skip 1 using 2:4:6 with yerrorbars lt rgb "red"   lw 1 title "Desvio Padrão"

set output "rtt_ramp_vs_level_cliente2.png"
set title "RTT Médio vs Nível (Rampa) — Cliente 2"
set xlabel "Nível da Rampa"
set ylabel "RTT (ms)"
plot   "stats_ramp_cliente2.csv" skip 1 using 2:4 with linespoints lt rgb "green"  lw 2 pt 7 title "Média",   ""                         skip 1 using 2:4:6 with yerrorbars lt rgb "magenta" lw 1 title "Desvio Padrão"
```

Para gerar todos os PNGs, execute:

```bash
gnuplot plot_commands.gnuplot
```

Isso criará na raiz:

```
rtt_vs_size_cliente1.png
rtt_vs_size_cliente2.png
rtt_ramp_vs_level_cliente1.png
rtt_ramp_vs_level_cliente2.png
```

---

## 12. Interpretação dos Resultados

### 12.1 Experimento 1 – RTT vs Tamanho

- Analise como o RTT varia com o tamanho do payload.  
- Compare comportamento em 10 Mb/s versus 100 Mb/s.  
- Observe o efeito de pacotes próximos ao limite UDP (65507 bytes).

### 12.2 Experimento 2 – RTT vs Taxa de Rampa

- Identifique a saturação da rede conforme a taxa aumenta.  
- Observe como o RTT se degrada em taxas cada vez mais altas.  
- Compare novamente 10 Mb/s versus 100 Mb/s.

---
