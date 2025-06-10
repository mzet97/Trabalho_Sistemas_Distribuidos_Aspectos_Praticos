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
print("Gerando gráficos interpretativos a partir dos dados de rede")
print("="*60)

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.max_open_warning'] = 0
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12

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

def subamostragem_inteligente(df, max_pontos=15):
    """Reduz o número de pontos mantendo os mais importantes"""
    if len(df) <= max_pontos:
        return df
    
    tamanhos = df['tamanho_bytes'].unique()
    tamanhos_sorted = np.sort(tamanhos)
    
    if len(tamanhos_sorted) <= max_pontos:
        return df
    
    indices = np.logspace(0, np.log10(len(tamanhos_sorted)-1), max_pontos, dtype=int)
    indices = np.unique(indices)
    
    tamanhos_selecionados = tamanhos_sorted[indices]
    return df[df['tamanho_bytes'].isin(tamanhos_selecionados)]

def formatar_bytes(bytes_val):
    """Formata valores de bytes para exibição mais legível"""
    if bytes_val < 1024:
        return f"{bytes_val}B"
    elif bytes_val < 1024**2:
        return f"{bytes_val//1024}KB"
    else:
        return f"{bytes_val//1024//1024}MB"

def criar_stats_rede_agregados():
    """Cria estatísticas de rede agregadas a partir dos dados dos clientes"""
    try:
        arquivos_10mbps = []
        arquivos_100mbps = []
        
        if verificar_arquivo("stats_cliente1.csv"):
            arquivos_10mbps.append("stats_cliente1.csv")
        if verificar_arquivo("stats_cliente2.csv"):
            arquivos_10mbps.append("stats_cliente2.csv")
        if verificar_arquivo("stats_cliente1_100.csv"):
            arquivos_100mbps.append("stats_cliente1_100.csv")
        if verificar_arquivo("stats_cliente2_100.csv"):
            arquivos_100mbps.append("stats_cliente2_100.csv")
        
        def agregar_dados(arquivos, sufixo):
            if not arquivos:
                return None
            
            dados_agregados = []
            for arquivo in arquivos:
                df = carregar_dados(arquivo)
                if df is not None:
                    dados_agregados.append(df)
            
            if not dados_agregados:
                return None
            
            df_agregado = pd.concat(dados_agregados, ignore_index=True)
            
            stats = df_agregado.groupby('tamanho_bytes').agg({
                'media_ms': 'mean',
                'jitter_ms': 'mean',
                'p95_ms': 'mean',
                'p99_ms': 'mean',
                'taxa_perda_%': 'mean'
            }).reset_index()
            
            stats = stats.rename(columns={
                'media_ms': 'media_agregada_ms',
                'jitter_ms': 'jitter_agregado_ms',
                'p95_ms': 'p95_agregado_ms',
                'p99_ms': 'p99_agregado_ms',
                'taxa_perda_%': 'taxa_perda_agregada_%'
            })
            
            arquivo_saida = f"stats_network_{sufixo}.csv"
            stats.to_csv(arquivo_saida, index=False)
            print(f" Criado: {arquivo_saida}")
            return stats
        
        if arquivos_10mbps:
            agregar_dados(arquivos_10mbps, "10mbps")
        if arquivos_100mbps:
            agregar_dados(arquivos_100mbps, "100mbps")
            
    except Exception as e:
        print(f" Erro ao criar stats agregados: {e}")

os.makedirs('graficos', exist_ok=True)

print("\n=== INICIANDO GERAÇÃO DE GRÁFICOS ===")
print()

print("0. Verificando/criando estatísticas de rede...")
if not (verificar_arquivo("stats_network_10mbps.csv") and verificar_arquivo("stats_network_100mbps.csv")):
    print(" Arquivos de rede não encontrados, tentando criar...")
    criar_stats_rede_agregados()

print("\n1. Gerando: RTT vs Tamanho - Cliente 1 (10 Mbps) [Simplificado]")
try:
    if verificar_arquivo("stats_cliente1.csv"):
        df = carregar_dados("stats_cliente1.csv")
        if df is not None:
            df_sub = subamostragem_inteligente(df, 12)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            ax.errorbar(df_sub['tamanho_bytes'], df_sub['media_ms'], 
                        yerr=df_sub['media_ms'] * 0.1,
                        fmt='o-', color='#FF6B35', linewidth=2.5, markersize=6, 
                        capsize=4, capthick=1.5, label='RTT Médio ± 10%')
            
            ax.set_xscale('log', base=2)
            ax.set_title('RTT vs Tamanho de Payload - Cliente 1 (10 Mbps)', 
                        fontsize=14, fontweight='bold', pad=20)
            ax.set_xlabel('Tamanho do Payload', fontsize=12)
            ax.set_ylabel('RTT (ms)', fontsize=12)
            ax.grid(True, alpha=0.3, linestyle='--')
            
            xticks = df_sub['tamanho_bytes'].values
            ax.set_xticks(xticks)
            ax.set_xticklabels([formatar_bytes(x) for x in xticks], rotation=45)
            
            ax.legend(frameon=True, fancybox=True, shadow=True)
            plt.tight_layout()
            plt.savefig('graficos/01_rtt_cliente1_10mbps.png', dpi=300, bbox_inches='tight')
            plt.close()
            print(" 01_rtt_cliente1_10mbps.png (simplificado)")
    else:
        print(" Arquivo stats_cliente1.csv não encontrado")
except Exception as e:
    print(f" Erro: {e}")

print("\n2. Gerando: RTT vs Tamanho - Cliente 1 (100 Mbps) [Simplificado]")
try:
    if verificar_arquivo("stats_cliente1_100.csv"):
        df = carregar_dados("stats_cliente1_100.csv")
        if df is not None:
            df_sub = subamostragem_inteligente(df, 12)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            ax.errorbar(df_sub['tamanho_bytes'], df_sub['media_ms'], 
                        yerr=df_sub['media_ms'] * 0.1,
                        fmt='s-', color='#004CFF', linewidth=2.5, markersize=6, 
                        capsize=4, capthick=1.5, label='RTT Médio ± 10%')
            
            ax.set_xscale('log', base=2)
            ax.set_title('RTT vs Tamanho de Payload - Cliente 1 (100 Mbps)', 
                        fontsize=14, fontweight='bold', pad=20)
            ax.set_xlabel('Tamanho do Payload', fontsize=12)
            ax.set_ylabel('RTT (ms)', fontsize=12)
            ax.grid(True, alpha=0.3, linestyle='--')
            
            xticks = df_sub['tamanho_bytes'].values
            ax.set_xticks(xticks)
            ax.set_xticklabels([formatar_bytes(x) for x in xticks], rotation=45)
            
            ax.legend(frameon=True, fancybox=True, shadow=True)
            plt.tight_layout()
            plt.savefig('graficos/02_rtt_cliente1_100mbps.png', dpi=300, bbox_inches='tight')
            plt.close()
            print(" 02_rtt_cliente1_100mbps.png (simplificado)")
    else:
        print(" Arquivo stats_cliente1_100.csv não encontrado")
except Exception as e:
    print(f" Erro: {e}")

print("\n3. Gerando: Comparação Direta RTT (10 vs 100 Mbps)")
try:
    if (verificar_arquivo("stats_network_10mbps.csv") and 
        verificar_arquivo("stats_network_100mbps.csv")):
        df_10 = carregar_dados("stats_network_10mbps.csv")
        df_100 = carregar_dados("stats_network_100mbps.csv")
        if df_10 is not None and df_100 is not None:
            df_10_sub = subamostragem_inteligente(df_10, 10)
            df_100_sub = subamostragem_inteligente(df_100, 10)
            
            fig, ax = plt.subplots(figsize=(12, 7))
            
            ax.plot(df_10_sub['tamanho_bytes'], df_10_sub['media_agregada_ms'], 
                    'o-', color='#FF1744', linewidth=3, markersize=8, 
                    label='10 Mbps', markeredgecolor='white', markeredgewidth=1)
            ax.plot(df_100_sub['tamanho_bytes'], df_100_sub['media_agregada_ms'], 
                    's-', color='#00C853', linewidth=3, markersize=8, 
                    label='100 Mbps', markeredgecolor='white', markeredgewidth=1)
            
            ax.set_xscale('log', base=2)
            ax.set_title('Comparação de RTT: Impacto da Largura de Banda', 
                        fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Tamanho do Payload', fontsize=13)
            ax.set_ylabel('RTT Médio (ms)', fontsize=13)
            ax.grid(True, alpha=0.3, linestyle='--')
            
            common_sizes = np.intersect1d(df_10_sub['tamanho_bytes'], df_100_sub['tamanho_bytes'])
            if len(common_sizes) > 0:
                ax.set_xticks(common_sizes[:10])
                ax.set_xticklabels([formatar_bytes(x) for x in common_sizes[:10]], rotation=45)
            
            ax.legend(frameon=True, fancybox=True, shadow=True, fontsize=12)
            plt.tight_layout()
            plt.savefig('graficos/03_comparacao_rtt_redes.png', dpi=300, bbox_inches='tight')
            plt.close()
            print(" 03_comparacao_rtt_redes.png (versão limpa)")
    else:
        if (verificar_arquivo("stats_cliente1.csv") and 
            verificar_arquivo("stats_cliente1_100.csv")):
            df_10 = carregar_dados("stats_cliente1.csv")
            df_100 = carregar_dados("stats_cliente1_100.csv")
            if df_10 is not None and df_100 is not None:
                df_10_sub = subamostragem_inteligente(df_10, 10)
                df_100_sub = subamostragem_inteligente(df_100, 10)
                
                fig, ax = plt.subplots(figsize=(12, 7))
                
                ax.plot(df_10_sub['tamanho_bytes'], df_10_sub['media_ms'], 
                        'o-', color='#FF1744', linewidth=3, markersize=8, 
                        label='Cliente 1 - 10 Mbps', markeredgecolor='white', markeredgewidth=1)
                ax.plot(df_100_sub['tamanho_bytes'], df_100_sub['media_ms'], 
                        's-', color='#00C853', linewidth=3, markersize=8, 
                        label='Cliente 1 - 100 Mbps', markeredgecolor='white', markeredgewidth=1)
                
                ax.set_xscale('log', base=2)
                ax.set_title('Comparação de RTT: 10 vs 100 Mbps (Cliente 1)', 
                            fontsize=16, fontweight='bold', pad=20)
                ax.set_xlabel('Tamanho do Payload', fontsize=13)
                ax.set_ylabel('RTT Médio (ms)', fontsize=13)
                ax.grid(True, alpha=0.3, linestyle='--')
                
                common_sizes = np.intersect1d(df_10_sub['tamanho_bytes'], df_100_sub['tamanho_bytes'])
                if len(common_sizes) > 0:
                    ax.set_xticks(common_sizes[:10])
                    ax.set_xticklabels([formatar_bytes(x) for x in common_sizes[:10]], rotation=45)
                
                ax.legend(frameon=True, fancybox=True, shadow=True, fontsize=12)
                plt.tight_layout()
                plt.savefig('graficos/03_comparacao_rtt_redes.png', dpi=300, bbox_inches='tight')
                plt.close()
                print(" 03_comparacao_rtt_redes.png (usando Cliente 1, versão limpa)")
        else:
            print(" Nenhum arquivo compatível encontrado")
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
                    color='#D84315', linewidth=2, markersize=5, label='Rede 10 Mbps')
            ax.plot(df_100['tamanho_bytes'], df_100['taxa_perda_agregada_%'], 's-', 
                    color='#1565C0', linewidth=2, markersize=5, label='Rede 100 Mbps')
            ax.set_xscale('log', base=2)
            ax.set_ylim(0, 100)
            ax.set_title('Comparação de Taxa de Perda: 10 Mbps vs 100 Mbps', 
                        fontsize=14, fontweight='bold')
            ax.set_xlabel('Tamanho do Payload (bytes)', fontsize=12)
            ax.set_ylabel('Taxa de Perda (%)', fontsize=12)
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.legend()
            plt.tight_layout()
            plt.savefig('graficos/04_comparacao_perda_redes.png', dpi=300, bbox_inches='tight')
            plt.close()
            print(" 04_comparacao_perda_redes.png")
    else:
        if (verificar_arquivo("stats_cliente1.csv") and 
            verificar_arquivo("stats_cliente1_100.csv")):
            df_10 = carregar_dados("stats_cliente1.csv")
            df_100 = carregar_dados("stats_cliente1_100.csv")
            if df_10 is not None and df_100 is not None:
                fig, ax = plt.subplots(figsize=(12, 8))
                perda_col = 'taxa_perda_%' if 'taxa_perda_%' in df_10.columns else None
                if perda_col:
                    ax.plot(df_10['tamanho_bytes'], df_10[perda_col], 'o-', 
                            color='#D84315', linewidth=2, markersize=5, label='Cliente 1 - 10 Mbps')
                    ax.plot(df_100['tamanho_bytes'], df_100[perda_col], 's-', 
                            color='#1565C0', linewidth=2, markersize=5, label='Cliente 1 - 100 Mbps')
                    ax.set_xscale('log', base=2)
                    ax.set_ylim(0, 100)
                    ax.set_title('Comparação de Taxa de Perda: 10 Mbps vs 100 Mbps (Cliente 1)', 
                                fontsize=14, fontweight='bold')
                    ax.set_xlabel('Tamanho do Payload (bytes)', fontsize=12)
                    ax.set_ylabel('Taxa de Perda (%)', fontsize=12)
                    ax.grid(True, alpha=0.3, linestyle='--')
                    ax.legend()
                    plt.tight_layout()
                    plt.savefig('graficos/04_comparacao_perda_redes.png', dpi=300, bbox_inches='tight')
                    plt.close()
                    print(" 04_comparacao_perda_redes.png (usando dados do Cliente 1)")
                else:
                    print(" Coluna de taxa de perda não encontrada")
        else:
            print(" Nenhum arquivo compatível encontrado")
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
                    color='#E91E63', linewidth=2, label='Rede 10 Mbps')
            ax.plot(df_10['tamanho_bytes'], df_10['jitter_agregado_ms'], 'o', 
                    color='#E91E63', markersize=3, alpha=0.7)
            ax.plot(df_100['tamanho_bytes'], df_100['jitter_agregado_ms'], '-', 
                    color='#4CAF50', linewidth=2, label='Rede 100 Mbps')
            ax.plot(df_100['tamanho_bytes'], df_100['jitter_agregado_ms'], 's', 
                    color='#4CAF50', markersize=3, alpha=0.7)
            ax.set_xscale('log', base=2)
            ax.set_title('Comparação de Jitter Médio: 10 Mbps vs 100 Mbps', 
                        fontsize=14, fontweight='bold')
            ax.set_xlabel('Tamanho do Payload (bytes)', fontsize=12)
            ax.set_ylabel('Jitter Médio (ms)', fontsize=12)
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.legend()
            plt.tight_layout()
            plt.savefig('graficos/05_comparacao_jitter_redes.png', dpi=300, bbox_inches='tight')
            plt.close()
            print(" 05_comparacao_jitter_redes.png")
    else:
        if (verificar_arquivo("stats_cliente1.csv") and 
            verificar_arquivo("stats_cliente1_100.csv")):
            df_10 = carregar_dados("stats_cliente1.csv")
            df_100 = carregar_dados("stats_cliente1_100.csv")
            if df_10 is not None and df_100 is not None:
                jitter_col = 'jitter_ms' if 'jitter_ms' in df_10.columns else None
                if jitter_col:
                    fig, ax = plt.subplots(figsize=(12, 8))
                    ax.plot(df_10['tamanho_bytes'], df_10[jitter_col], '-', 
                            color='#E91E63', linewidth=2, label='Cliente 1 - 10 Mbps')
                    ax.plot(df_10['tamanho_bytes'], df_10[jitter_col], 'o', 
                            color='#E91E63', markersize=3, alpha=0.7)
                    ax.plot(df_100['tamanho_bytes'], df_100[jitter_col], '-', 
                            color='#4CAF50', linewidth=2, label='Cliente 1 - 100 Mbps')
                    ax.plot(df_100['tamanho_bytes'], df_100[jitter_col], 's', 
                            color='#4CAF50', markersize=3, alpha=0.7)
                    ax.set_xscale('log', base=2)
                    ax.set_title('Comparação de Jitter Médio: 10 Mbps vs 100 Mbps (Cliente 1)', 
                                fontsize=14, fontweight='bold')
                    ax.set_xlabel('Tamanho do Payload (bytes)', fontsize=12)
                    ax.set_ylabel('Jitter Médio (ms)', fontsize=12)
                    ax.grid(True, alpha=0.3, linestyle='--')
                    ax.legend()
                    plt.tight_layout()
                    plt.savefig('graficos/05_comparacao_jitter_redes.png', dpi=300, bbox_inches='tight')
                    plt.close()
                    print(" 05_comparacao_jitter_redes.png (usando dados do Cliente 1)")
                else:
                    print(" Coluna de jitter não encontrada")
        else:
            print(" Nenhum arquivo compatível encontrado")
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
                    color='#FF5722', linewidth=2, label='10 Mbps - P95')
            ax.plot(df_10['tamanho_bytes'], df_10['p99_agregado_ms'], '--', 
                    color='#FF5722', linewidth=2, label='10 Mbps - P99')
            ax.plot(df_100['tamanho_bytes'], df_100['p95_agregado_ms'], '-', 
                    color='#2196F3', linewidth=2, label='100 Mbps - P95')
            ax.plot(df_100['tamanho_bytes'], df_100['p99_agregado_ms'], '--', 
                    color='#2196F3', linewidth=2, label='100 Mbps - P99')
            ax.set_xscale('log', base=2)
            ax.set_title('Comparação de Percentis P95 e P99', 
                        fontsize=14, fontweight='bold')
            ax.set_xlabel('Tamanho do Payload (bytes)', fontsize=12)
            ax.set_ylabel('RTT (ms)', fontsize=12)
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.legend()
            plt.tight_layout()
            plt.savefig('graficos/06_comparacao_percentis.png', dpi=300, bbox_inches='tight')
            plt.close()
            print(" 06_comparacao_percentis.png")
    else:
        if (verificar_arquivo("stats_cliente1.csv") and 
            verificar_arquivo("stats_cliente1_100.csv")):
            df_10 = carregar_dados("stats_cliente1.csv")
            df_100 = carregar_dados("stats_cliente1_100.csv")
            if df_10 is not None and df_100 is not None:
                fig, ax = plt.subplots(figsize=(12, 8))
                ax.plot(df_10['tamanho_bytes'], df_10['p95_ms'], '-', 
                        color='#FF5722', linewidth=2, label='Cliente 1 10 Mbps - P95')
                ax.plot(df_10['tamanho_bytes'], df_10['p99_ms'], '--', 
                        color='#FF5722', linewidth=2, label='Cliente 1 10 Mbps - P99')
                ax.plot(df_100['tamanho_bytes'], df_100['p95_ms'], '-', 
                        color='#2196F3', linewidth=2, label='Cliente 1 100 Mbps - P95')
                ax.plot(df_100['tamanho_bytes'], df_100['p99_ms'], '--', 
                        color='#2196F3', linewidth=2, label='Cliente 1 100 Mbps - P99')
                ax.set_xscale('log', base=2)
                ax.set_title('Comparação de Percentis P95 e P99 (Cliente 1)', 
                            fontsize=14, fontweight='bold')
                ax.set_xlabel('Tamanho do Payload (bytes)', fontsize=12)
                ax.set_ylabel('RTT (ms)', fontsize=12)
                ax.grid(True, alpha=0.3, linestyle='--')
                ax.legend()
                plt.tight_layout()
                plt.savefig('graficos/06_comparacao_percentis.png', dpi=300, bbox_inches='tight')
                plt.close()
                print(" 06_comparacao_percentis.png (usando dados do Cliente 1)")
        else:
            print(" Nenhum arquivo compatível encontrado")
except Exception as e:
    print(f" Erro: {e}")

print("\n7. Gerando: Dashboard Resumido")
try:
    if (verificar_arquivo("stats_network_10mbps.csv") and 
        verificar_arquivo("stats_network_100mbps.csv")):
        df_10 = carregar_dados("stats_network_10mbps.csv")
        df_100 = carregar_dados("stats_network_100mbps.csv")
        if df_10 is not None and df_100 is not None:
            df_10_sub = subamostragem_inteligente(df_10, 8)
            df_100_sub = subamostragem_inteligente(df_100, 8)
            
            fig, axes = plt.subplots(2, 2, figsize=(14, 10))
            fig.suptitle('Dashboard Comparativo: 10 Mbps vs 100 Mbps', 
                        fontsize=16, fontweight='bold')
            
            colors_10 = '#B71C1C'
            colors_100 = '#1B5E20'
            
            ax = axes[0, 0]
            ax.plot(df_10_sub['tamanho_bytes'], df_10_sub['media_agregada_ms'], 
                    'o-', color=colors_10, linewidth=2.5, markersize=6, label='10 Mbps')
            ax.plot(df_100_sub['tamanho_bytes'], df_100_sub['media_agregada_ms'], 
                    's-', color=colors_100, linewidth=2.5, markersize=6, label='100 Mbps')
            ax.set_xscale('log', base=2)
            ax.set_title('RTT Médio', fontweight='bold')
            ax.set_ylabel('RTT (ms)')
            ax.grid(True, alpha=0.3)
            ax.legend()
            
            ax = axes[0, 1]
            ax.plot(df_10_sub['tamanho_bytes'], df_10_sub['taxa_perda_agregada_%'], 
                    'o-', color=colors_10, linewidth=2.5, markersize=6, label='10 Mbps')
            ax.plot(df_100_sub['tamanho_bytes'], df_100_sub['taxa_perda_agregada_%'], 
                    's-', color=colors_100, linewidth=2.5, markersize=6, label='100 Mbps')
            ax.set_xscale('log', base=2)
            ax.set_ylim(0, max(df_10_sub['taxa_perda_agregada_%'].max(), 
                              df_100_sub['taxa_perda_agregada_%'].max()) * 1.1)
            ax.set_title('Taxa de Perda', fontweight='bold')
            ax.set_ylabel('Perda (%)')
            ax.grid(True, alpha=0.3)
            ax.legend()
            
            ax = axes[1, 0]
            ax.plot(df_10_sub['tamanho_bytes'], df_10_sub['jitter_agregado_ms'], 
                    'o-', color=colors_10, linewidth=2.5, markersize=6, label='10 Mbps')
            ax.plot(df_100_sub['tamanho_bytes'], df_100_sub['jitter_agregado_ms'], 
                    's-', color=colors_100, linewidth=2.5, markersize=6, label='100 Mbps')
            ax.set_xscale('log', base=2)
            ax.set_title('Jitter', fontweight='bold')
            ax.set_xlabel('Tamanho do Payload')
            ax.set_ylabel('Jitter (ms)')
            ax.grid(True, alpha=0.3)
            ax.legend()
            
            ax = axes[1, 1]
            merged = pd.merge(df_10_sub, df_100_sub, on='tamanho_bytes', suffixes=('_10', '_100'))
            if not merged.empty:
                speedup = merged['media_agregada_ms_10'] / merged['media_agregada_ms_100']
                ax.plot(merged['tamanho_bytes'], speedup, 'o-', 
                        color='#FF9800', linewidth=2.5, markersize=6, label='Speedup')
                ax.axhline(y=1, color='black', linestyle='--', alpha=0.5)
                ax.set_xscale('log', base=2)
                ax.set_title('Speedup (RTT 10Mbps / RTT 100Mbps)', fontweight='bold')
                ax.set_xlabel('Tamanho do Payload')
                ax.set_ylabel('Fator de Melhoria')
                ax.grid(True, alpha=0.3)
                ax.legend()
            
            for ax in axes.flat:
                if hasattr(ax, 'get_xticks'):
                    xticks = ax.get_xticks()
                    valid_ticks = [x for x in xticks if x >= 1][:6]
                    ax.set_xticks(valid_ticks)
                    ax.set_xticklabels([formatar_bytes(int(x)) for x in valid_ticks], rotation=45)
            
            plt.tight_layout()
            plt.savefig('graficos/07_dashboard_rede_comparativo.png', dpi=300, bbox_inches='tight')
            plt.close()
            print(" 07_dashboard_rede_comparativo.png (versão limpa)")
    else:
        print(" Arquivos de rede agregados não encontrados, pulando dashboard")
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
                        fmt='o-', color='#C62828', linewidth=2, markersize=4, 
                        capsize=3, label='10 Mbps (IC 98%)')
            ax.errorbar(df_100['tamanho_bytes'], df_100['media_ms'], 
                        yerr=[df_100['media_ms'] - df_100['ic_lower_ms'], 
                              df_100['ic_upper_ms'] - df_100['media_ms']],
                        fmt='s-', color='#2E7D32', linewidth=2, markersize=4, 
                        capsize=3, label='100 Mbps (IC 98%)')
            ax.set_xscale('log', base=2)
            ax.set_title('Cliente 1: Comparação entre Redes 10 e 100 Mbps', 
                        fontsize=14, fontweight='bold')
            ax.set_xlabel('Tamanho do Payload (bytes)', fontsize=12)
            ax.set_ylabel('RTT Médio (ms)', fontsize=12)
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.legend()
            plt.tight_layout()
            plt.savefig('graficos/08_cliente1_comparacao_rede.png', dpi=300, bbox_inches='tight')
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
                        fmt='o-', color='#6A1B9A', linewidth=2, markersize=4, 
                        capsize=3, label='10 Mbps (IC 98%)')
            ax.errorbar(df_100['tamanho_bytes'], df_100['media_ms'], 
                        yerr=[df_100['media_ms'] - df_100['ic_lower_ms'], 
                              df_100['ic_upper_ms'] - df_100['media_ms']],
                        fmt='s-', color='#F57F17', linewidth=2, markersize=4, 
                        capsize=3, label='100 Mbps (IC 98%)')
            ax.set_xscale('log', base=2)
            ax.set_title('Cliente 2: Comparação entre Redes 10 e 100 Mbps', 
                        fontsize=14, fontweight='bold')
            ax.set_xlabel('Tamanho do Payload (bytes)', fontsize=12)
            ax.set_ylabel('RTT Médio (ms)', fontsize=12)
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.legend()
            plt.tight_layout()
            plt.savefig('graficos/09_cliente2_comparacao_rede.png', dpi=300, bbox_inches='tight')
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
            nivel_col = 'nivel' if 'nivel' in df_10.columns else df_10.columns[1]
            rtt_col = 'media_ms' if 'media_ms' in df_10.columns else df_10.columns[3]
            
            df_10_1k = df_10[df_10['tamanho_bytes'] == 1024].copy()
            df_100_1k = df_100[df_100['tamanho_bytes'] == 1024].copy()
            if not df_10_1k.empty and not df_100_1k.empty:
                fig, ax = plt.subplots(figsize=(12, 8))
                ax.plot(df_10_1k[nivel_col], df_10_1k[rtt_col], '-', 
                        color='#AD1457', linewidth=2, label='10 Mbps (suavizado)')
                ax.plot(df_10_1k[nivel_col], df_10_1k[rtt_col], 'o', 
                        color='#AD1457', markersize=3, alpha=0.7, label='10 Mbps (pontos)')
                ax.plot(df_100_1k[nivel_col], df_100_1k[rtt_col], '-', 
                        color='#00695C', linewidth=2, label='100 Mbps (suavizado)')
                ax.plot(df_100_1k[nivel_col], df_100_1k[rtt_col], 's', 
                        color='#00695C', markersize=3, alpha=0.7, label='100 Mbps (pontos)')
                ax.set_xlim(1, 19)
                ax.set_title('Rampa - Cliente 1: RTT vs Nível de Carga (1KB)', 
                            fontsize=14, fontweight='bold')
                ax.set_xlabel('Nível da Rampa (1=10 req/s → 10=100 req/s → 19=10 req/s)', 
                              fontsize=12)
                ax.set_ylabel('RTT Médio (ms)', fontsize=12)
                ax.grid(True, alpha=0.3, linestyle='--')
                ax.legend()
                plt.tight_layout()
                plt.savefig('graficos/10_ramp_cliente1_rtt_carga.png', dpi=300, bbox_inches='tight')
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
            nivel_col = 'nivel' if 'nivel' in df_10.columns else df_10.columns[1]
            perda_col = 'taxa_perda_%' if 'taxa_perda_%' in df_10.columns else (
                df_10.columns[13] if len(df_10.columns) > 13 else df_10.columns[-1])
            
            df_10_1k = df_10[df_10['tamanho_bytes'] == 1024].copy()
            df_100_1k = df_100[df_100['tamanho_bytes'] == 1024].copy()
            df_10_64k = df_10[df_10['tamanho_bytes'] == 65507].copy()
            df_100_64k = df_100[df_100['tamanho_bytes'] == 65507].copy()
            fig, ax = plt.subplots(figsize=(12, 8))
            
            if not df_10_1k.empty:
                ax.plot(df_10_1k[nivel_col], df_10_1k[perda_col], 'o-', 
                        color='#E53935', linewidth=2, markersize=4, label='10 Mbps - 1KB')
            if not df_100_1k.empty:
                ax.plot(df_100_1k[nivel_col], df_100_1k[perda_col], 's-', 
                        color='#43A047', linewidth=2, markersize=4, label='100 Mbps - 1KB')
            if not df_10_64k.empty:
                ax.plot(df_10_64k[nivel_col], df_10_64k[perda_col], 'o--', 
                        color='#FF8A80', linewidth=2, markersize=4, label='10 Mbps - 64KB')
            if not df_100_64k.empty:
                ax.plot(df_100_64k[nivel_col], df_100_64k[perda_col], 's--', 
                        color='#A5D6A7', linewidth=2, markersize=4, label='100 Mbps - 64KB')
            ax.set_xlim(1, 19)
            ax.set_ylim(0, 100)
            ax.set_title('Taxa de Perda vs Nível de Rampa - Cliente 1', 
                        fontsize=14, fontweight='bold')
            ax.set_xlabel('Nível da Rampa', fontsize=12)
            ax.set_ylabel('Taxa de Perda (%)', fontsize=12)
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.legend()
            plt.tight_layout()
            plt.savefig('graficos/11_ramp_perda_vs_nivel.png', dpi=300, bbox_inches='tight')
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
            
            nivel_col = 'nivel' if 'nivel' in df_10.columns else df_10.columns[1]
            rtt_col = 'media_ms' if 'media_ms' in df_10.columns else df_10.columns[3]
            
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
                        color='#D32F2F', linewidth=2, label='10 Mbps - 2 bytes')
            if not df_100_2b.empty:
                ax.plot(df_100_2b[nivel_col], df_100_2b['rtt_normalizado'], '-', 
                        color='#388E3C', linewidth=2, label='100 Mbps - 2 bytes')
            if not df_10_1k.empty:
                ax.plot(df_10_1k[nivel_col], df_10_1k['rtt_normalizado'], '--', 
                        color='#8BC34A', linewidth=2, label='10 Mbps - 1KB')
            if not df_100_1k.empty:
                ax.plot(df_100_1k[nivel_col], df_100_1k['rtt_normalizado'], '--', 
                        color='#FF5722', linewidth=2, label='100 Mbps - 1KB')
            if not df_10_64k.empty:
                ax.plot(df_10_64k[nivel_col], df_10_64k['rtt_normalizado'], ':', 
                        color='#9C27B0', linewidth=2, label='10 Mbps - 64KB')
            if not df_100_64k.empty:
                ax.plot(df_100_64k[nivel_col], df_100_64k['rtt_normalizado'], ':', 
                        color='#FFC107', linewidth=2, label='100 Mbps - 64KB')
            ax.set_xlim(1, 19)
            ax.set_ylim(0.5, 5)
            ax.set_title('Análise de Saturação: RTT Normalizado por Nível', 
                        fontsize=14, fontweight='bold')
            ax.set_xlabel('Nível da Rampa', fontsize=12)
            ax.set_ylabel('RTT Normalizado (RTT/RTT_inicial)', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            plt.savefig('graficos/12_analise_saturacao.png', dpi=300, bbox_inches='tight')
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
    caminho = os.path.join('graficos', grafico)
    if os.path.exists(caminho):
        total_gerados += 1
        tamanho = os.path.getsize(caminho)
        print(f"  Ok {grafico} ({tamanho:,} bytes)")
    else:
        print(f"  Não OK {grafico} (não gerado)")

print()
print(f" Total de gráficos gerados: {total_gerados}/{len(graficos_gerados)}")

if os.path.exists('graficos'):
    arquivos = os.listdir('graficos')
    total_size = sum(os.path.getsize(os.path.join('graficos', f)) 
                     for f in arquivos if f.endswith('.png'))
    print(f" Tamanho total: {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")

print()
print("="*60)
print("Todos os gráficos estão no diretório 'graficos/'")
print("="*60)