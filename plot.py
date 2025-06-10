#!/usr/bin/env python3

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')

print("="*60)
print("Gerando gráficos em português a partir dos dados de rede")
print("="*60)

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.max_open_warning'] = 0

def verificar_arquivo(nome_arquivo):
    return os.path.exists(nome_arquivo)

def carregar_dados(arquivo):
    try:
        df = pd.read_csv(arquivo)
        df = df.dropna()
        return df
    except Exception as e:
        print(f" Erro ao carregar {arquivo}: {e}")
        return None

os.makedirs('graficos', exist_ok=True)

print("\n=== INICIANDO GERAÇÃO DE GRÁFICOS ===")
print()

print("1. Gerando: RTT vs Tamanho - Cliente 1 (10 Mbps)")
try:
    if verificar_arquivo("stats_cliente1.csv"):
        df = carregar_dados("stats_cliente1.csv")
        if df is not None:
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.errorbar(df['tamanho_bytes'], df['media_ms'], 
                        yerr=[df['media_ms'] - df['ic_lower_ms'], df['ic_upper_ms'] - df['media_ms']],
                        fmt='o-', color='#1f77b4', linewidth=2, markersize=5, 
                        capsize=3, label='RTT Médio (IC 98%)')
            ax.plot(df['tamanho_bytes'], df['p95_ms'], '--', 
                    color='#ff7f0e', linewidth=2, label='Percentil 95')
            ax.plot(df['tamanho_bytes'], df['p99_ms'], ':', 
                    color='#d62728', linewidth=2, label='Percentil 99')
            ax.set_xscale('log', base=2)
            ax.set_title('RTT vs Tamanho de Payload - Cliente 1 (Rede 10 Mbps)', 
                        fontsize=14, fontweight='bold')
            ax.set_xlabel('Tamanho do Payload (bytes)', fontsize=12)
            ax.set_ylabel('RTT (ms)', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.legend()
            plt.tight_layout()
            plt.savefig('graficos_portugues/01_rtt_cliente1_10mbps.png', dpi=300, bbox_inches='tight')
            plt.close()
            print(" 01_rtt_cliente1_10mbps.png")
    else:
        print(" Arquivo stats_cliente1.csv não encontrado")
except Exception as e:
    print(f" Erro: {e}")

print("\n2. Gerando: RTT vs Tamanho - Cliente 1 (100 Mbps)")
try:
    if verificar_arquivo("stats_cliente1_100.csv"):
        df = carregar_dados("stats_cliente1_100.csv")
        if df is not None:
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.errorbar(df['tamanho_bytes'], df['media_ms'], 
                        yerr=[df['media_ms'] - df['ic_lower_ms'], df['ic_upper_ms'] - df['media_ms']],
                        fmt='s-', color='#2ca02c', linewidth=2, markersize=5, 
                        capsize=3, label='RTT Médio (IC 98%)')
            ax.plot(df['tamanho_bytes'], df['p95_ms'], '--', 
                    color='#ff9900', linewidth=2, label='Percentil 95')
            ax.plot(df['tamanho_bytes'], df['p99_ms'], ':', 
                    color='#cc3300', linewidth=2, label='Percentil 99')
            ax.set_xscale('log', base=2)
            ax.set_title('RTT vs Tamanho de Payload - Cliente 1 (Rede 100 Mbps)', 
                        fontsize=14, fontweight='bold')
            ax.set_xlabel('Tamanho do Payload (bytes)', fontsize=12)
            ax.set_ylabel('RTT (ms)', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.legend()
            plt.tight_layout()
            plt.savefig('graficos_portugues/02_rtt_cliente1_100mbps.png', dpi=300, bbox_inches='tight')
            plt.close()
            print(" 02_rtt_cliente1_100mbps.png")
    else:
        print(" Arquivo stats_cliente1_100.csv não encontrado")
except Exception as e:
    print(f" Erro: {e}")

print("\n3. Gerando: Comparação de RTT Médio (10 vs 100 Mbps)")
try:
    if (verificar_arquivo("stats_network_10mbps.csv") and 
        verificar_arquivo("stats_network_100mbps.csv")):
        df_10 = carregar_dados("stats_network_10mbps.csv")
        df_100 = carregar_dados("stats_network_100mbps.csv")
        if df_10 is not None and df_100 is not None:
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.plot(df_10['tamanho_bytes'], df_10['media_agregada_ms'], 'o-', 
                    color='#1f77b4', linewidth=2, markersize=5, label='Rede 10 Mbps')
            ax.plot(df_100['tamanho_bytes'], df_100['media_agregada_ms'], 's-', 
                    color='#ff7f0e', linewidth=2, markersize=5, label='Rede 100 Mbps')
            ax.set_xscale('log', base=2)
            ax.set_title('Comparação de RTT Médio: 10 Mbps vs 100 Mbps', 
                        fontsize=14, fontweight='bold')
            ax.set_xlabel('Tamanho do Payload (bytes)', fontsize=12)
            ax.set_ylabel('RTT Médio (ms)', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.legend()
            plt.tight_layout()
            plt.savefig('graficos_portugues/03_comparacao_rtt_redes.png', dpi=300, bbox_inches='tight')
            plt.close()
            print(" 03_comparacao_rtt_redes.png")
    else:
        print(" Arquivos de rede não encontrados")
except Exception as e:
    print(f" Erro: {e}")

print("\n4. Gerando: Comparação de Taxa de Perda (10 vs 100 Mbps)")
try:
    if (verificar_arquivo("stats_network_10mbps.csv") and 
        verificar_arquivo("stats_network_100mbps.csv")):
        df_10 = carregar_dados("stats_network_10mbps.csv")
        df_100 = carregar_dados("stats_network_100mbps.csv")
        if df_10 is not None and df_100 is not None:
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.plot(df_10['tamanho_bytes'], df_10['taxa_perda_agregada_%'], 'o-', 
                    color='#d62728', linewidth=2, markersize=5, label='Rede 10 Mbps')
            ax.plot(df_100['tamanho_bytes'], df_100['taxa_perda_agregada_%'], 's-', 
                    color='#2ca02c', linewidth=2, markersize=5, label='Rede 100 Mbps')
            ax.set_xscale('log', base=2)
            ax.set_ylim(0, 100)
            ax.set_title('Comparação de Taxa de Perda: 10 Mbps vs 100 Mbps', 
                        fontsize=14, fontweight='bold')
            ax.set_xlabel('Tamanho do Payload (bytes)', fontsize=12)
            ax.set_ylabel('Taxa de Perda (%)', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.legend()
            plt.tight_layout()
            plt.savefig('graficos_portugues/04_comparacao_perda_redes.png', dpi=300, bbox_inches='tight')
            plt.close()
            print(" 04_comparacao_perda_redes.png")
    else:
        print(" Arquivos de rede não encontrados")
except Exception as e:
    print(f" Erro: {e}")

print("\n5. Gerando: Comparação de Jitter Médio (10 vs 100 Mbps)")
try:
    if (verificar_arquivo("stats_network_10mbps.csv") and 
        verificar_arquivo("stats_network_100mbps.csv")):
        df_10 = carregar_dados("stats_network_10mbps.csv")
        df_100 = carregar_dados("stats_network_100mbps.csv")
        if df_10 is not None and df_100 is not None:
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.plot(df_10['tamanho_bytes'], df_10['jitter_agregado_ms'], '-', 
                    color='#9467bd', linewidth=2, label='Rede 10 Mbps')
            ax.plot(df_10['tamanho_bytes'], df_10['jitter_agregado_ms'], 'o', 
                    color='#9467bd', markersize=3, alpha=0.7)
            ax.plot(df_100['tamanho_bytes'], df_100['jitter_agregado_ms'], '-', 
                    color='#8c564b', linewidth=2, label='Rede 100 Mbps')
            ax.plot(df_100['tamanho_bytes'], df_100['jitter_agregado_ms'], 's', 
                    color='#8c564b', markersize=3, alpha=0.7)
            ax.set_xscale('log', base=2)
            ax.set_title('Comparação de Jitter Médio: 10 Mbps vs 100 Mbps', 
                        fontsize=14, fontweight='bold')
            ax.set_xlabel('Tamanho do Payload (bytes)', fontsize=12)
            ax.set_ylabel('Jitter Médio (ms)', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.legend()
            plt.tight_layout()
            plt.savefig('graficos_portugues/05_comparacao_jitter_redes.png', dpi=300, bbox_inches='tight')
            plt.close()
            print(" 05_comparacao_jitter_redes.png")
    else:
        print(" Arquivos de rede não encontrados")
except Exception as e:
    print(f" Erro: {e}")

print("\n6. Gerando: Comparação de Percentis P95 e P99")
try:
    if (verificar_arquivo("stats_network_10mbps.csv") and 
        verificar_arquivo("stats_network_100mbps.csv")):
        df_10 = carregar_dados("stats_network_10mbps.csv")
        df_100 = carregar_dados("stats_network_100mbps.csv")
        if df_10 is not None and df_100 is not None:
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.plot(df_10['tamanho_bytes'], df_10['p95_agregado_ms'], '-', 
                    color='#d62728', linewidth=2, label='10 Mbps - P95')
            ax.plot(df_10['tamanho_bytes'], df_10['p99_agregado_ms'], '--', 
                    color='#d62728', linewidth=2, label='10 Mbps - P99')
            ax.plot(df_100['tamanho_bytes'], df_100['p95_agregado_ms'], '-', 
                    color='#2ca02c', linewidth=2, label='100 Mbps - P95')
            ax.plot(df_100['tamanho_bytes'], df_100['p99_agregado_ms'], '--', 
                    color='#2ca02c', linewidth=2, label='100 Mbps - P99')
            ax.set_xscale('log', base=2)
            ax.set_title('Comparação de Percentis P95 e P99', 
                        fontsize=14, fontweight='bold')
            ax.set_xlabel('Tamanho do Payload (bytes)', fontsize=12)
            ax.set_ylabel('RTT (ms)', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.legend()
            plt.tight_layout()
            plt.savefig('graficos_portugues/06_comparacao_percentis.png', dpi=300, bbox_inches='tight')
            plt.close()
            print(" 06_comparacao_percentis.png")
    else:
        print(" Arquivos de rede não encontrados")
except Exception as e:
    print(f" Erro: {e}")

print("\n7. Gerando: Dashboard Comparativo de Rede")
try:
    if (verificar_arquivo("stats_network_10mbps.csv") and 
        verificar_arquivo("stats_network_100mbps.csv")):
        df_10 = carregar_dados("stats_network_10mbps.csv")
        df_100 = carregar_dados("stats_network_100mbps.csv")
        if df_10 is not None and df_100 is not None:
            fig, axes = plt.subplots(3, 2, figsize=(15, 12))
            fig.suptitle('Dashboard Comparativo: Rede 10 Mbps vs 100 Mbps', 
                        fontsize=16, fontweight='bold')
            ax = axes[0, 0]
            ax.plot(df_10['tamanho_bytes'], df_10['media_agregada_ms'], 'o-', 
                    color='#1f77b4', linewidth=2, markersize=3, label='10 Mbps')
            ax.plot(df_100['tamanho_bytes'], df_100['media_agregada_ms'], 's-', 
                    color='#ff7f0e', linewidth=2, markersize=3, label='100 Mbps')
            ax.set_xscale('log', base=2)
            ax.set_title('RTT Médio por Tamanho', fontsize=12, fontweight='bold')
            ax.set_xlabel('Tamanho (bytes)')
            ax.set_ylabel('RTT (ms)')
            ax.grid(True, alpha=0.3)
            ax.legend()
            ax = axes[0, 1]
            ax.plot(df_10['tamanho_bytes'], df_10['taxa_perda_agregada_%'], 'o-', 
                    color='#d62728', linewidth=2, markersize=3, label='10 Mbps')
            ax.plot(df_100['tamanho_bytes'], df_100['taxa_perda_agregada_%'], 's-', 
                    color='#2ca02c', linewidth=2, markersize=3, label='100 Mbps')
            ax.set_xscale('log', base=2)
            ax.set_ylim(0, 100)
            ax.set_title('Taxa de Perda', fontsize=12, fontweight='bold')
            ax.set_xlabel('Tamanho (bytes)')
            ax.set_ylabel('Perda (%)')
            ax.grid(True, alpha=0.3)
            ax.legend()
            ax = axes[1, 0]
            ax.plot(df_10['tamanho_bytes'], df_10['jitter_agregado_ms'], 'o-', 
                    color='#9467bd', linewidth=2, markersize=3, label='10 Mbps')
            ax.plot(df_100['tamanho_bytes'], df_100['jitter_agregado_ms'], 's-', 
                    color='#8c564b', linewidth=2, markersize=3, label='100 Mbps')
            ax.set_xscale('log', base=2)
            ax.set_title('Jitter', fontsize=12, fontweight='bold')
            ax.set_xlabel('Tamanho (bytes)')
            ax.set_ylabel('Jitter (ms)')
            ax.grid(True, alpha=0.3)
            ax.legend()
            ax = axes[1, 1]
            ax.plot(df_10['tamanho_bytes'], df_10['p95_agregada_ms'], 'o-', 
                    color='#17becf', linewidth=2, markersize=3, label='10 Mbps')
            ax.plot(df_100['tamanho_bytes'], df_100['p95_agregada_ms'], 's-', 
                    color='#bcbd22', linewidth=2, markersize=3, label='100 Mbps')
            ax.set_xscale('log', base=2)
            ax.set_title('Percentil 95', fontsize=12, fontweight='bold')
            ax.set_xlabel('Tamanho (bytes)')
            ax.set_ylabel('P95 (ms)')
            ax.grid(True, alpha=0.3)
            ax.legend()
            ax = axes[2, 0]
            ax.plot(df_10['tamanho_bytes'], df_10['p99_agregada_ms'], 'o-', 
                    color='#e377c2', linewidth=2, markersize=3, label='10 Mbps')
            ax.plot(df_100['tamanho_bytes'], df_100['p99_agregada_ms'], 's-', 
                    color='#7f7f7f', linewidth=2, markersize=3, label='100 Mbps')
            ax.set_xscale('log', base=2)
            ax.set_title('Percentil 99', fontsize=12, fontweight='bold')
            ax.set_xlabel('Tamanho (bytes)')
            ax.set_ylabel('P99 (ms)')
            ax.grid(True, alpha=0.3)
            ax.legend()
            ax = axes[2, 1]
            merged = pd.merge(df_10, df_100, on='tamanho_bytes', suffixes=('_10', '_100'))
            speedup = merged['media_agregada_ms_10'] / merged['media_agregada_ms_100']
            ax.plot(merged['tamanho_bytes'], speedup, 'o-', 
                    color='#ff7f0e', linewidth=2, markersize=3, label='Speedup')
            ax.set_xscale('log', base=2)
            ax.set_title('Speedup: RTT(10Mbps) / RTT(100Mbps)', fontsize=12, fontweight='bold')
            ax.set_xlabel('Tamanho (bytes)')
            ax.set_ylabel('Razão')
            ax.grid(True, alpha=0.3)
            ax.legend()
            plt.tight_layout()
            plt.savefig('graficos_portugues/07_dashboard_rede_comparativo.png', dpi=300, bbox_inches='tight')
            plt.close()
            print(" 07_dashboard_rede_comparativo.png")
    else:
        print(" Arquivos de rede não encontrados")
except Exception as e:
    print(f" Erro: {e}")

print("\n8. Gerando: Cliente 1 - Comparação entre Redes")
try:
    if (verificar_arquivo("stats_cliente1.csv") and 
        verificar_arquivo("stats_cliente1_100.csv")):
        df_10 = carregar_dados("stats_cliente1.csv")
        df_100 = carregar_dados("stats_cliente1_100.csv")
        if df_10 is not None and df_100 is not None:
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.errorbar(df_10['tamanho_bytes'], df_10['media_ms'], 
                        yerr=[df_10['media_ms'] - df_10['ic_lower_ms'], 
                              df_10['ic_upper_ms'] - df_10['media_ms']],
                        fmt='o-', color='#1f77b4', linewidth=2, markersize=4, 
                        capsize=3, label='10 Mbps (IC 98%)')
            ax.errorbar(df_100['tamanho_bytes'], df_100['media_ms'], 
                        yerr=[df_100['media_ms'] - df_100['ic_lower_ms'], 
                              df_100['ic_upper_ms'] - df_100['media_ms']],
                        fmt='s-', color='#ff7f0e', linewidth=2, markersize=4, 
                        capsize=3, label='100 Mbps (IC 98%)')
            ax.set_xscale('log', base=2)
            ax.set_title('Cliente 1: Comparação entre Redes 10 e 100 Mbps', 
                        fontsize=14, fontweight='bold')
            ax.set_xlabel('Tamanho do Payload (bytes)', fontsize=12)
            ax.set_ylabel('RTT Médio (ms)', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.legend()
            plt.tight_layout()
            plt.savefig('graficos_portugues/08_cliente1_comparacao_rede.png', dpi=300, bbox_inches='tight')
            plt.close()
            print(" 08_cliente1_comparacao_rede.png")
    else:
        print(" Arquivos do cliente 1 não encontrados")
except Exception as e:
    print(f" Erro: {e}")

print("\n9. Gerando: Cliente 2 - Comparação entre Redes")
try:
    if (verificar_arquivo("stats_cliente2.csv") and 
        verificar_arquivo("stats_cliente2_100.csv")):
        df_10 = carregar_dados("stats_cliente2.csv")
        df_100 = carregar_dados("stats_cliente2_100.csv")
        if df_10 is not None and df_100 is not None:
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.errorbar(df_10['tamanho_bytes'], df_10['media_ms'], 
                        yerr=[df_10['media_ms'] - df_10['ic_lower_ms'], 
                              df_10['ic_upper_ms'] - df_10['media_ms']],
                        fmt='o-', color='#2ca02c', linewidth=2, markersize=4, 
                        capsize=3, label='10 Mbps (IC 98%)')
            ax.errorbar(df_100['tamanho_bytes'], df_100['media_ms'], 
                        yerr=[df_100['media_ms'] - df_100['ic_lower_ms'], 
                              df_100['ic_upper_ms'] - df_100['media_ms']],
                        fmt='s-', color='#d62728', linewidth=2, markersize=4, 
                        capsize=3, label='100 Mbps (IC 98%)')
            ax.set_xscale('log', base=2)
            ax.set_title('Cliente 2: Comparação entre Redes 10 e 100 Mbps', 
                        fontsize=14, fontweight='bold')
            ax.set_xlabel('Tamanho do Payload (bytes)', fontsize=12)
            ax.set_ylabel('RTT Médio (ms)', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.legend()
            plt.tight_layout()
            plt.savefig('graficos_portugues/09_cliente2_comparacao_rede.png', dpi=300, bbox_inches='tight')
            plt.close()
            print(" 09_cliente2_comparacao_rede.png")
    else:
        print(" Arquivos do cliente 2 não encontrados")
except Exception as e:
    print(f" Erro: {e}")

print("\n10. Gerando: Rampa Cliente 1 - RTT vs Nível de Carga")
try:
    if (verificar_arquivo("stats_ramp_cliente1.csv") and 
        verificar_arquivo("stats_ramp_cliente1_100.csv")):
        df_10 = carregar_dados("stats_ramp_cliente1.csv")
        df_100 = carregar_dados("stats_ramp_cliente1_100.csv")
        if df_10 is not None and df_100 is not None:
            df_10_1k = df_10[df_10['tamanho_bytes'] == 1024].copy()
            df_100_1k = df_100[df_100['tamanho_bytes'] == 1024].copy()
            if not df_10_1k.empty and not df_100_1k.empty:
                fig, ax = plt.subplots(figsize=(12, 8))
                ax.plot(df_10_1k[nivel_col], df_10_1k[rtt_col], '-', 
                        color='#1f77b4', linewidth=2, label='10 Mbps (suavizado)')
                ax.plot(df_10_1k[nivel_col], df_10_1k[rtt_col], 'o', 
                        color='#1f77b4', markersize=3, alpha=0.7, label='10 Mbps (pontos)')
                ax.plot(df_100_1k[nivel_col], df_100_1k[rtt_col], '-', 
                        color='#ff7f0e', linewidth=2, label='100 Mbps (suavizado)')
                ax.plot(df_100_1k[nivel_col], df_100_1k[rtt_col], 's', 
                        color='#ff7f0e', markersize=3, alpha=0.7, label='100 Mbps (pontos)')
                ax.set_xlim(1, 19)
                ax.set_title('Rampa - Cliente 1: RTT vs Nível de Carga (1KB)', 
                            fontsize=14, fontweight='bold')
                ax.set_xlabel('Nível da Rampa (1=10 req/s → 10=100 req/s → 19=10 req/s)', 
                              fontsize=12)
                ax.set_ylabel('RTT Médio (ms)', fontsize=12)
                ax.grid(True, alpha=0.3)
                ax.legend()
                plt.tight_layout()
                plt.savefig('graficos_portugues/10_ramp_cliente1_rtt_carga.png', dpi=300, bbox_inches='tight')
                plt.close()
                print(" 10_ramp_cliente1_rtt_carga.png")
            else:
                print(" Dados para 1KB não encontrados nos arquivos de rampa")
    else:
        print(" Arquivos de rampa do cliente 1 não encontrados")
except Exception as e:
    print(f" Erro: {e}")

print("\n11. Gerando: Taxa de Perda vs Nível de Rampa")
try:
    if (verificar_arquivo("stats_ramp_cliente1.csv") and 
        verificar_arquivo("stats_ramp_cliente1_100.csv")):
        df_10 = carregar_dados("stats_ramp_cliente1.csv")
        df_100 = carregar_dados("stats_ramp_cliente1_100.csv")
        if df_10 is not None and df_100 is not None:
            df_10_1k = df_10[df_10['tamanho_bytes'] == 1024].copy()
            df_100_1k = df_100[df_100['tamanho_bytes'] == 1024].copy()
            df_10_64k = df_10[df_10['tamanho_bytes'] == 65507].copy()
            df_100_64k = df_100[df_100['tamanho_bytes'] == 65507].copy()
            fig, ax = plt.subplots(figsize=(12, 8))
            nivel_col = df_10.columns[1]
            perda_col = df_10.columns[13] if len(df_10.columns) > 13 else df_10.columns[-1]
            if not df_10_1k.empty:
                ax.plot(df_10_1k[nivel_col], df_10_1k[perda_col], 'o-', 
                        color='#1f77b4', linewidth=2, markersize=4, label='10 Mbps - 1KB')
            if not df_100_1k.empty:
                ax.plot(df_100_1k[nivel_col], df_100_1k[perda_col], 's-', 
                        color='#ff7f0e', linewidth=2, markersize=4, label='100 Mbps - 1KB')
            if not df_10_64k.empty:
                ax.plot(df_10_64k[nivel_col], df_10_64k[perda_col], 'o--', 
                        color='lightblue', linewidth=2, markersize=4, label='10 Mbps - 64KB')
            if not df_100_64k.empty:
                ax.plot(df_100_64k[nivel_col], df_100_64k[perda_col], 's--', 
                        color='orange', linewidth=2, markersize=4, label='100 Mbps - 64KB')
            ax.set_xlim(1, 19)
            ax.set_ylim(0, 100)
            ax.set_title('Taxa de Perda vs Nível de Rampa - Cliente 1', 
                        fontsize=14, fontweight='bold')
            ax.set_xlabel('Nível da Rampa', fontsize=12)
            ax.set_ylabel('Taxa de Perda (%)', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.legend()
            plt.tight_layout()
            plt.savefig('graficos_portugues/11_ramp_perda_vs_nivel.png', dpi=300, bbox_inches='tight')
            plt.close()
            print(" 11_ramp_perda_vs_nivel.png")
    else:
        print(" Arquivos de rampa não encontrados")
except Exception as e:
    print(f" Erro: {e}")

print("\n12. Gerando: Análise de Saturação - RTT Normalizado")
try:
    if (verificar_arquivo("stats_ramp_cliente1.csv") and 
        verificar_arquivo("stats_ramp_cliente1_100.csv")):
        df_10 = carregar_dados("stats_ramp_cliente1.csv")
        df_100 = carregar_dados("stats_ramp_cliente1_100.csv")
        if df_10 is not None and df_100 is not None:
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.axhline(y=1.5, color='black', linestyle='--', linewidth=2, alpha=0.7)
            ax.text(10, 1.6, 'Limiar de Saturação (150%)', ha='center', fontsize=10)
            nivel_col = df_10.columns[1]
            rtt_col = df_10.columns[3]
            def normalizar_rtt(df, tamanho):
                df_filtered = df[df['tamanho_bytes'] == tamanho].copy()
                if df_filtered.empty:
                    return pd.DataFrame()
                base_rtt = df_filtered[rtt_col].iloc[0]
                if base_rtt > 0:
                    df_filtered['rtt_normalizado'] = df_filtered[rtt_col] / base_rtt
                    return df_filtered
                return pd.DataFrame()
            df_10_2b = normalizar_rtt(df_10, 2)
            df_100_2b = normalizar_rtt(df_100, 2)
            df_10_1k = normalizar_rtt(df_10, 1024)
            df_100_1k = normalizar_rtt(df_100, 1024)
            df_10_64k = normalizar_rtt(df_10, 65507)
            df_100_64k = normalizar_rtt(df_100, 65507)
            if not df_10_2b.empty:
                ax.plot(df_10_2b[nivel_col], df_10_2b['rtt_normalizado'], '-', 
                        color='#ff0000', linewidth=2, label='10 Mbps - 2 bytes')
            if not df_100_2b.empty:
                ax.plot(df_100_2b[nivel_col], df_100_2b['rtt_normalizado'], '-', 
                        color='#00ff00', linewidth=2, label='100 Mbps - 2 bytes')
            if not df_10_1k.empty:
                ax.plot(df_10_1k[nivel_col], df_10_1k['rtt_normalizado'], '--', 
                        color='#cc0000', linewidth=2, label='10 Mbps - 1KB')
            if not df_100_1k.empty:
                ax.plot(df_100_1k[nivel_col], df_100_1k['rtt_normalizado'], '--', 
                        color='#009900', linewidth=2, label='100 Mbps - 1KB')
            if not df_10_64k.empty:
                ax.plot(df_10_64k[nivel_col], df_10_64k['rtt_normalizado'], ':', 
                        color='#990000', linewidth=2, label='10 Mbps - 64KB')
            if not df_100_64k.empty:
                ax.plot(df_100_64k[nivel_col], df_100_64k['rtt_normalizado'], ':', 
                        color='#006600', linewidth=2, label='100 Mbps - 64KB')
            ax.set_xlim(1, 19)
            ax.set_ylim(0.5, 5)
            ax.set_title('Análise de Saturação: RTT Normalizado por Nível', 
                        fontsize=14, fontweight='bold')
            ax.set_xlabel('Nível da Rampa', fontsize=12)
            ax.set_ylabel('RTT Normalizado (RTT/RTT_inicial)', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            plt.savefig('graficos_portugues/12_analise_saturacao.png', dpi=300, bbox_inches='tight')
            plt.close()
            print(" 12_analise_saturacao.png")
    else:
        print(" Arquivos de rampa não encontrados")
except Exception as e:
    print(f" Erro: {e}")

print("\n=== GERAÇÃO DE GRÁFICOS CONCLUÍDA ===")
print()

graficos_gerados = [
    '01_rtt_cliente1_10mbps.png',
    '02_rtt_cliente1_100mbps.png', 
    '03_comparacao_rtt_redes.png',
    '04_comparacao_perda_redes.png',
    '05_comparacao_jitter_redes.png',
    '06_comparacao_percentis.png',
    '07_dashboard_rede_comparativo.png',
    '08_cliente1_comparacao_rede.png',
    '09_cliente2_comparacao_rede.png',
    '10_ramp_cliente1_rtt_carga.png',
    '11_ramp_perda_vs_nivel.png',
    '12_analise_saturacao.png'
]

total_gerados = 0
for grafico in graficos_gerados:
    caminho = os.path.join('graficos_portugues', grafico)
    if os.path.exists(caminho):
        total_gerados += 1
        tamanho = os.path.getsize(caminho)
        print(f"  Ok {grafico} ({tamanho:,} bytes)")
    else:
        print(f"  Não OK {grafico} (não gerado)")

print()
print(f" Total de gráficos gerados: {total_gerados}/{len(graficos_gerados)}")

if os.path.exists('graficos_portugues'):
    arquivos = os.listdir('graficos_portugues')
    total_size = sum(os.path.getsize(os.path.join('graficos_portugues', f)) 
                     for f in arquivos if f.endswith('.png'))
    print(f" Tamanho total: {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")

print()
print("="*60)
print("MIGRAÇÃO GNUPLOT → PYTHON CONCLUÍDA!")
print("Todos os gráficos estão em português no diretório 'graficos_portugues/'")
print("Gráficos equivalentes aos do plot_commands.gnuplot mas com estilo português")
print("="*60)