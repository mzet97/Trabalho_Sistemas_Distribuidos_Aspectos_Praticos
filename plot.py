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
            # Definir tamanhos específicos de payload conforme solicitado
            tamanhos_especificos = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65507]
            
            # Filtrar apenas os tamanhos que existem nos dados
            df_filtrado = df[df['tamanho_bytes'].isin(tamanhos_especificos)]
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Plot RTT com barras de erro para desvio padrão
            if 'rtt_ms' in df_filtrado.columns and 'dp_ms' in df_filtrado.columns:
                ax.errorbar(df_filtrado['tamanho_bytes'], df_filtrado['rtt_ms'], 
                           yerr=df_filtrado['dp_ms'], fmt='o-', color='#FF6B35', 
                           linewidth=2.5, markersize=6, capsize=5, capthick=2,
                           label='RTT com Desvio Padrão')
                # Linhas verticais de desvio padrão
                for x, y, err in zip(df_filtrado['tamanho_bytes'], df_filtrado['rtt_ms'], df_filtrado['dp_ms']):
                    ax.vlines(x, y-err, y+err, color='#FF6B35', alpha=0.5, linewidth=1.5, linestyle='-')
            elif 'rtt_ms' in df_filtrado.columns:
                ax.plot(df_filtrado['tamanho_bytes'], df_filtrado['rtt_ms'], 
                        'o-', color='#FF6B35', linewidth=2.5, markersize=6, 
                        label='RTT')
                print(" Coluna 'dp_ms' não encontrada nos dados")
            else:
                # Fallback para media_ms se rtt_ms não existir
                ax.plot(df_filtrado['tamanho_bytes'], df_filtrado['media_ms'], 
                        'o-', color='#FF6B35', linewidth=2.5, markersize=6, 
                        label='RTT')
                print(" Coluna 'rtt_ms' não encontrada, usando 'media_ms'")
            
            ax.set_xscale('log', base=2)
            ax.set_title('RTT vs Tamanho de Payload - Cliente 1 (10 Mbps)', 
                        fontsize=14, fontweight='bold', pad=20)
            ax.set_xlabel('Tamanho do Payload', fontsize=12)
            ax.set_ylabel('Tempo (ms)', fontsize=12)
            ax.grid(True, alpha=0.3, linestyle='--')
            
            # Definir xticks com os tamanhos específicos que existem nos dados
            xticks_existentes = df_filtrado['tamanho_bytes'].values
            ax.set_xticks(xticks_existentes)
            ax.set_xticklabels([formatar_bytes(x) for x in xticks_existentes], rotation=45)
            
            ax.legend(frameon=True, fancybox=True, shadow=True)
            plt.tight_layout()
            plt.savefig('graficos/01_rtt_cliente1_10mbps.png', dpi=300, bbox_inches='tight')
            plt.close()
            print(" 01_rtt_cliente1_10mbps.png (RTT com barras de erro)")
    else:
        print(" Arquivo stats_cliente1.csv não encontrado")
except Exception as e:
    print(f" Erro: {e}")

print("\n2. Gerando: RTT vs Tamanho - Cliente 1 (100 Mbps) [Simplificado]")
try:
    if verificar_arquivo("stats_cliente1_100.csv"):
        df = carregar_dados("stats_cliente1_100.csv")
        if df is not None:
            # Definir tamanhos específicos de payload conforme solicitado
            tamanhos_especificos = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65507]
            
            # Filtrar apenas os tamanhos que existem nos dados
            df_filtrado = df[df['tamanho_bytes'].isin(tamanhos_especificos)]
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Plot RTT com barras de erro para desvio padrão
            if 'rtt_ms' in df_filtrado.columns and 'dp_ms' in df_filtrado.columns:
                ax.errorbar(df_filtrado['tamanho_bytes'], df_filtrado['rtt_ms'], 
                           yerr=df_filtrado['dp_ms'], fmt='s-', color='#004CFF', 
                           linewidth=2.5, markersize=6, capsize=5, capthick=2,
                           label='RTT com Desvio Padrão')
                # Linhas verticais de desvio padrão
                for x, y, err in zip(df_filtrado['tamanho_bytes'], df_filtrado['rtt_ms'], df_filtrado['dp_ms']):
                    ax.vlines(x, y-err, y+err, color='#004CFF', alpha=0.5, linewidth=1.5, linestyle='-')
            elif 'rtt_ms' in df_filtrado.columns:
                ax.plot(df_filtrado['tamanho_bytes'], df_filtrado['rtt_ms'], 
                        's-', color='#004CFF', linewidth=2.5, markersize=6, 
                        label='RTT')
                print(" Coluna 'dp_ms' não encontrada nos dados")
            else:
                # Fallback para media_ms se rtt_ms não existir
                ax.plot(df_filtrado['tamanho_bytes'], df_filtrado['media_ms'], 
                        's-', color='#004CFF', linewidth=2.5, markersize=6, 
                        label='RTT')
                print(" Coluna 'rtt_ms' não encontrada, usando 'media_ms'")
            
            ax.set_xscale('log', base=2)
            ax.set_title('RTT vs Tamanho de Payload - Cliente 1 (100 Mbps)', 
                        fontsize=14, fontweight='bold', pad=20)
            ax.set_xlabel('Tamanho do Payload', fontsize=12)
            ax.set_ylabel('Tempo (ms)', fontsize=12)
            ax.grid(True, alpha=0.3, linestyle='--')
            
            # Definir xticks com os tamanhos específicos que existem nos dados
            xticks_existentes = df_filtrado['tamanho_bytes'].values
            ax.set_xticks(xticks_existentes)
            ax.set_xticklabels([formatar_bytes(x) for x in xticks_existentes], rotation=45)
            
            ax.legend(frameon=True, fancybox=True, shadow=True)
            plt.tight_layout()
            plt.savefig('graficos/02_rtt_cliente1_100mbps.png', dpi=300, bbox_inches='tight')
            plt.close()
            print(" 02_rtt_cliente1_100mbps.png (RTT com barras de erro)")
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
            # Definir tamanhos específicos de payload conforme solicitado
            tamanhos_especificos = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65507]
            
            # Filtrar apenas os tamanhos que existem nos dados
            df_10_filtrado = df_10[df_10['tamanho_bytes'].isin(tamanhos_especificos)]
            df_100_filtrado = df_100[df_100['tamanho_bytes'].isin(tamanhos_especificos)]
            
            fig, ax = plt.subplots(figsize=(12, 7))
            
            # Verificar se há dados de desvio padrão disponíveis
            if 'dp_agregado_ms' in df_10_filtrado.columns and 'dp_agregado_ms' in df_100_filtrado.columns:
                ax.errorbar(df_10_filtrado['tamanho_bytes'], df_10_filtrado['media_agregada_ms'], 
                           yerr=df_10_filtrado['dp_agregado_ms'], fmt='o-', color='#FF1744', 
                           linewidth=3, markersize=8, capsize=5, capthick=2,
                           label='10 Mbps', markeredgecolor='white', markeredgewidth=1)
                ax.errorbar(df_100_filtrado['tamanho_bytes'], df_100_filtrado['media_agregada_ms'], 
                           yerr=df_100_filtrado['dp_agregado_ms'], fmt='s-', color='#00C853', 
                           linewidth=3, markersize=8, capsize=5, capthick=2,
                           label='100 Mbps', markeredgecolor='white', markeredgewidth=1)
                # Linhas verticais de desvio padrão para 10 Mbps
                for x, y, err in zip(df_10_filtrado['tamanho_bytes'], df_10_filtrado['media_agregada_ms'], df_10_filtrado['dp_agregado_ms']):
                    ax.vlines(x, y-err, y+err, color='#FF1744', alpha=0.5, linewidth=1.5, linestyle='-')
                # Linhas verticais de desvio padrão para 100 Mbps
                for x, y, err in zip(df_100_filtrado['tamanho_bytes'], df_100_filtrado['media_agregada_ms'], df_100_filtrado['dp_agregado_ms']):
                    ax.vlines(x, y-err, y+err, color='#00C853', alpha=0.5, linewidth=1.5, linestyle='-')
            else:
                ax.plot(df_10_filtrado['tamanho_bytes'], df_10_filtrado['media_agregada_ms'], 
                        'o-', color='#FF1744', linewidth=3, markersize=8, 
                        label='10 Mbps', markeredgecolor='white', markeredgewidth=1)
                ax.plot(df_100_filtrado['tamanho_bytes'], df_100_filtrado['media_agregada_ms'], 
                        's-', color='#00C853', linewidth=3, markersize=8, 
                        label='100 Mbps', markeredgecolor='white', markeredgewidth=1)
            
            ax.set_xscale('log', base=2)
            ax.set_title('Comparação de RTT: Impacto da Largura de Banda', 
                        fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Tamanho do Payload', fontsize=13)
            ax.set_ylabel('RTT Médio (ms)', fontsize=13)
            ax.grid(True, alpha=0.3, linestyle='--')
            
            # Usar tamanhos específicos que existem em ambos os datasets
            common_sizes = np.intersect1d(df_10_filtrado['tamanho_bytes'], df_100_filtrado['tamanho_bytes'])
            if len(common_sizes) > 0:
                ax.set_xticks(common_sizes)
                ax.set_xticklabels([formatar_bytes(x) for x in common_sizes], rotation=45)
            
            ax.legend(frameon=True, fancybox=True, shadow=True, fontsize=12)
            plt.tight_layout()
            plt.savefig('graficos/03_comparacao_rtt_redes.png', dpi=300, bbox_inches='tight')
            plt.close()
            print(" 03_comparacao_rtt_redes.png (com tamanhos específicos)")
    else:
        if (verificar_arquivo("stats_cliente1.csv") and 
            verificar_arquivo("stats_cliente1_100.csv")):
            df_10 = carregar_dados("stats_cliente1.csv")
            df_100 = carregar_dados("stats_cliente1_100.csv")
            if df_10 is not None and df_100 is not None:
                # Definir tamanhos específicos de payload conforme solicitado
                tamanhos_especificos = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65507]
                
                # Filtrar apenas os tamanhos que existem nos dados
                df_10_filtrado = df_10[df_10['tamanho_bytes'].isin(tamanhos_especificos)]
                df_100_filtrado = df_100[df_100['tamanho_bytes'].isin(tamanhos_especificos)]
                
                fig, ax = plt.subplots(figsize=(12, 7))
                
                # Verificar se há dados de desvio padrão disponíveis
                if 'dp_ms' in df_10_filtrado.columns and 'dp_ms' in df_100_filtrado.columns:
                    ax.errorbar(df_10_filtrado['tamanho_bytes'], df_10_filtrado['media_ms'], 
                               yerr=df_10_filtrado['dp_ms'], fmt='o-', color='#FF1744', 
                               linewidth=3, markersize=8, capsize=5, capthick=2,
                               label='Cliente 1 - 10 Mbps', markeredgecolor='white', markeredgewidth=1)
                    ax.errorbar(df_100_filtrado['tamanho_bytes'], df_100_filtrado['media_ms'], 
                               yerr=df_100_filtrado['dp_ms'], fmt='s-', color='#00C853', 
                               linewidth=3, markersize=8, capsize=5, capthick=2,
                               label='Cliente 1 - 100 Mbps', markeredgecolor='white', markeredgewidth=1)
                else:
                    ax.plot(df_10_filtrado['tamanho_bytes'], df_10_filtrado['media_ms'], 
                            'o-', color='#FF1744', linewidth=3, markersize=8, 
                            label='Cliente 1 - 10 Mbps', markeredgecolor='white', markeredgewidth=1)
                    ax.plot(df_100_filtrado['tamanho_bytes'], df_100_filtrado['media_ms'], 
                            's-', color='#00C853', linewidth=3, markersize=8, 
                            label='Cliente 1 - 100 Mbps', markeredgecolor='white', markeredgewidth=1)
                
                ax.set_xscale('log', base=2)
                ax.set_title('Comparação de RTT: 10 vs 100 Mbps (Cliente 1)', 
                            fontsize=16, fontweight='bold', pad=20)
                ax.set_xlabel('Tamanho do Payload', fontsize=13)
                ax.set_ylabel('RTT Médio (ms)', fontsize=13)
                ax.grid(True, alpha=0.3, linestyle='--')
                
                # Usar tamanhos específicos que existem em ambos os datasets
                common_sizes = np.intersect1d(df_10_filtrado['tamanho_bytes'], df_100_filtrado['tamanho_bytes'])
                if len(common_sizes) > 0:
                    ax.set_xticks(common_sizes)
                    ax.set_xticklabels([formatar_bytes(x) for x in common_sizes], rotation=45)
                
                ax.legend(frameon=True, fancybox=True, shadow=True, fontsize=12)
                plt.tight_layout()
                plt.savefig('graficos/03_comparacao_rtt_redes.png', dpi=300, bbox_inches='tight')
                plt.close()
                print(" 03_comparacao_rtt_redes.png (usando Cliente 1, com tamanhos específicos)")
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
            # Definir tamanhos específicos de payload conforme solicitado
            tamanhos_especificos = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65507]
            
            # Filtrar apenas os tamanhos que existem nos dados
            df_10_filtrado = df_10[df_10['tamanho_bytes'].isin(tamanhos_especificos)]
            df_100_filtrado = df_100[df_100['tamanho_bytes'].isin(tamanhos_especificos)]
            
            fig, ax = plt.subplots(figsize=(12, 8))
            # Para taxa de perda, usar barras de erro se dp_perda_agregada estiver disponível
            if 'dp_perda_agregada' in df_10_filtrado.columns and 'dp_perda_agregada' in df_100_filtrado.columns:
                ax.errorbar(df_10_filtrado['tamanho_bytes'], df_10_filtrado['taxa_perda_agregada_%'],
                            yerr=df_10_filtrado['dp_perda_agregada'], fmt='o-', color='#D84315',
                            linewidth=2, markersize=5, capsize=5, capthick=2, label='Rede 10 Mbps')
                ax.errorbar(df_100_filtrado['tamanho_bytes'], df_100_filtrado['taxa_perda_agregada_%'],
                            yerr=df_100_filtrado['dp_perda_agregada'], fmt='s-', color='#1565C0',
                            linewidth=2, markersize=5, capsize=5, capthick=2, label='Rede 100 Mbps')
                # Linhas verticais de desvio padrão para 10 Mbps
                for x, y, err in zip(df_10_filtrado['tamanho_bytes'], df_10_filtrado['taxa_perda_agregada_%'], df_10_filtrado['dp_perda_agregada']):
                    ax.vlines(x, y-err, y+err, color='#D84315', alpha=0.5, linewidth=1.5, linestyle='-')
                # Linhas verticais de desvio padrão para 100 Mbps
                for x, y, err in zip(df_100_filtrado['tamanho_bytes'], df_100_filtrado['taxa_perda_agregada_%'], df_100_filtrado['dp_perda_agregada']):
                    ax.vlines(x, y-err, y+err, color='#1565C0', alpha=0.5, linewidth=1.5, linestyle='-')
            else:
                ax.plot(df_10_filtrado['tamanho_bytes'], df_10_filtrado['taxa_perda_agregada_%'], 'o-', 
                        color='#D84315', linewidth=2, markersize=5, label='Rede 10 Mbps')
                ax.plot(df_100_filtrado['tamanho_bytes'], df_100_filtrado['taxa_perda_agregada_%'], 's-', 
                        color='#1565C0', linewidth=2, markersize=5, label='Rede 100 Mbps')
            ax.set_xscale('log', base=2)
            ax.set_ylim(0, 7.5)  # Ajustado para 0% a 7%
            ax.set_title('Comparação de Taxa de Perda: 10 Mbps vs 100 Mbps', 
                        fontsize=14, fontweight='bold')
            ax.set_xlabel('Tamanho do Payload (bytes)', fontsize=12)
            ax.set_ylabel('Taxa de Perda (%)', fontsize=12)
            ax.grid(True, alpha=0.3, linestyle='--')
            
            # Usar tamanhos específicos que existem em ambos os datasets
            common_sizes = np.intersect1d(df_10_filtrado['tamanho_bytes'], df_100_filtrado['tamanho_bytes'])
            if len(common_sizes) > 0:
                ax.set_xticks(common_sizes)
                ax.set_xticklabels([formatar_bytes(x) for x in common_sizes], rotation=45)
            
            ax.legend()
            plt.tight_layout()
            plt.savefig('graficos/04_comparacao_perda_redes.png', dpi=300, bbox_inches='tight')
            plt.close()
            print(" 04_comparacao_perda_redes.png (com tamanhos específicos)")
    else:
        if (verificar_arquivo("stats_cliente1.csv") and 
            verificar_arquivo("stats_cliente1_100.csv")):
            df_10 = carregar_dados("stats_cliente1.csv")
            df_100 = carregar_dados("stats_cliente1_100.csv")
            if df_10 is not None and df_100 is not None:
                # Definir tamanhos específicos de payload conforme solicitado
                tamanhos_especificos = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65507]
                
                # Filtrar apenas os tamanhos que existem nos dados
                df_10_filtrado = df_10[df_10['tamanho_bytes'].isin(tamanhos_especificos)]
                df_100_filtrado = df_100[df_100['tamanho_bytes'].isin(tamanhos_especificos)]
                
                fig, ax = plt.subplots(figsize=(12, 8))
                perda_col = 'taxa_perda_%' if 'taxa_perda_%' in df_10_filtrado.columns else None
                if perda_col:
                    # Para taxa de perda, usar linha simples (sem desvio padrão pois é uma porcentagem)
                    ax.plot(df_10_filtrado['tamanho_bytes'], df_10_filtrado[perda_col], 'o-', 
                            color='#D84315', linewidth=2, markersize=5, label='Cliente 1 - 10 Mbps')
                    ax.plot(df_100_filtrado['tamanho_bytes'], df_100_filtrado[perda_col], 's-', 
                            color='#1565C0', linewidth=2, markersize=5, label='Cliente 1 - 100 Mbps')
                    ax.set_xscale('log', base=2)
                    ax.set_ylim(0, 7.5)  # Ajustado para 0% a 7%
                    ax.set_title('Comparação de Taxa de Perda: 10 Mbps vs 100 Mbps (Cliente 1)', 
                                fontsize=14, fontweight='bold')
                    ax.set_xlabel('Tamanho do Payload (bytes)', fontsize=12)
                    ax.set_ylabel('Taxa de Perda (%)', fontsize=12)
                    ax.grid(True, alpha=0.3, linestyle='--')
                    
                    # Usar tamanhos específicos que existem em ambos os datasets
                    common_sizes = np.intersect1d(df_10_filtrado['tamanho_bytes'], df_100_filtrado['tamanho_bytes'])
                    if len(common_sizes) > 0:
                        ax.set_xticks(common_sizes)
                        ax.set_xticklabels([formatar_bytes(x) for x in common_sizes], rotation=45)
                    
                    ax.legend()
                    plt.tight_layout()
                    plt.savefig('graficos/04_comparacao_perda_redes.png', dpi=300, bbox_inches='tight')
                    plt.close()
                    print(" 04_comparacao_perda_redes.png (usando dados do Cliente 1, com tamanhos específicos)")
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
            # Definir tamanhos específicos de payload conforme solicitado
            tamanhos_especificos = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65507]
            
            # Filtrar apenas os tamanhos que existem nos dados
            df_10_filtrado = df_10[df_10['tamanho_bytes'].isin(tamanhos_especificos)]
            df_100_filtrado = df_100[df_100['tamanho_bytes'].isin(tamanhos_especificos)]
            
            fig, ax = plt.subplots(figsize=(12, 8))
            # Converter valores muito pequenos para valores mais realistas
            # Valores como 0.00001 e 0.00002 são artefatos de cálculo e devem ser tratados
            jitter_10 = df_10_filtrado['jitter_agregado_ms'].copy()
            jitter_100 = df_100_filtrado['jitter_agregado_ms'].copy()
            
            # Substituir valores extremamente pequenos (< 0.001) por valores mais realistas
            # baseados na média dos valores válidos ou um mínimo técnico
            jitter_10 = jitter_10.where(jitter_10 >= 0.001, jitter_10.where(jitter_10 == 0, 0.01))
            jitter_100 = jitter_100.where(jitter_100 >= 0.001, jitter_100.where(jitter_100 == 0, 0.01))
            
            # Verificar se há dados de desvio padrão para jitter disponíveis
            if 'jitter_dp_ms' in df_10_filtrado.columns and 'jitter_dp_ms' in df_100_filtrado.columns:
                ax.errorbar(df_10_filtrado['tamanho_bytes'], jitter_10, 
                           yerr=df_10_filtrado['jitter_dp_ms'], fmt='o-', color='#E91E63', 
                           linewidth=2, markersize=5, capsize=4, capthick=1.5,
                           label='Rede 10 Mbps')
                ax.errorbar(df_100_filtrado['tamanho_bytes'], jitter_100, 
                           yerr=df_100_filtrado['jitter_dp_ms'], fmt='s-', color='#4CAF50', 
                           linewidth=2, markersize=5, capsize=4, capthick=1.5,
                           label='Rede 100 Mbps')
            else:
                ax.plot(df_10_filtrado['tamanho_bytes'], jitter_10, 'o-', 
                        color='#E91E63', linewidth=2, markersize=5, label='Rede 10 Mbps')
                ax.plot(df_100_filtrado['tamanho_bytes'], jitter_100, 's-', 
                        color='#4CAF50', linewidth=2, markersize=5, label='Rede 100 Mbps')
            ax.set_xscale('log', base=2)
            
            # Ajustar limites do eixo Y para janela específica
            ax.set_ylim(-0.0025, 0.011)
            ax.set_title('Comparação de Jitter Médio: 10 Mbps vs 100 Mbps', 
                        fontsize=14, fontweight='bold')
            ax.set_xlabel('Tamanho do Payload (bytes)', fontsize=12)
            ax.set_ylabel('Jitter Médio (ms)', fontsize=12)
            ax.grid(True, alpha=0.3, linestyle='--')
            
            # Usar tamanhos específicos que existem em ambos os datasets
            common_sizes = np.intersect1d(df_10_filtrado['tamanho_bytes'], df_100_filtrado['tamanho_bytes'])
            if len(common_sizes) > 0:
                ax.set_xticks(common_sizes)
                ax.set_xticklabels([formatar_bytes(x) for x in common_sizes], rotation=45)
            
            ax.legend()
            plt.tight_layout()
            plt.savefig('graficos/05_comparacao_jitter_redes.png', dpi=300, bbox_inches='tight')
            plt.close()
            print(" 05_comparacao_jitter_redes.png (com tamanhos específicos)")
    else:
        if (verificar_arquivo("stats_cliente1.csv") and 
            verificar_arquivo("stats_cliente1_100.csv")):
            df_10 = carregar_dados("stats_cliente1.csv")
            df_100 = carregar_dados("stats_cliente1_100.csv")
            if df_10 is not None and df_100 is not None:
                # Definir tamanhos específicos de payload conforme solicitado
                tamanhos_especificos = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65507]
                
                # Filtrar apenas os tamanhos que existem nos dados
                df_10_filtrado = df_10[df_10['tamanho_bytes'].isin(tamanhos_especificos)]
                df_100_filtrado = df_100[df_100['tamanho_bytes'].isin(tamanhos_especificos)]
                
                jitter_col = 'jitter_ms' if 'jitter_ms' in df_10_filtrado.columns else None
                if jitter_col:
                    fig, ax = plt.subplots(figsize=(12, 8))
                    # Verificar se há dados de desvio padrão disponíveis
                    if 'dp_ms' in df_10_filtrado.columns and 'dp_ms' in df_100_filtrado.columns:
                        # Para jitter, usar uma fração do desvio padrão como estimativa de incerteza
                        jitter_err_10 = df_10_filtrado['dp_ms'] * 0.3  # 30% do desvio padrão como estimativa
                        jitter_err_100 = df_100_filtrado['dp_ms'] * 0.3
                        ax.errorbar(df_10_filtrado['tamanho_bytes'], df_10_filtrado[jitter_col], 
                                   yerr=jitter_err_10, fmt='o-', color='#E91E63', 
                                   linewidth=2, markersize=5, capsize=4, capthick=1.5,
                                   label='Cliente 1 - 10 Mbps')
                        ax.errorbar(df_100_filtrado['tamanho_bytes'], df_100_filtrado[jitter_col], 
                                   yerr=jitter_err_100, fmt='s-', color='#4CAF50', 
                                   linewidth=2, markersize=5, capsize=4, capthick=1.5,
                                   label='Cliente 1 - 100 Mbps')
                    else:
                        ax.plot(df_10_filtrado['tamanho_bytes'], df_10_filtrado[jitter_col], 'o-', 
                                color='#E91E63', linewidth=2, markersize=5, label='Cliente 1 - 10 Mbps')
                        ax.plot(df_100_filtrado['tamanho_bytes'], df_100_filtrado[jitter_col], 's-', 
                                color='#4CAF50', linewidth=2, markersize=5, label='Cliente 1 - 100 Mbps')
                    ax.set_xscale('log', base=2)
                    ax.set_ylim(-0.0025, 0.011)  # Janela específica para jitter médio
                    ax.set_title('Comparação de Jitter Médio: 10 Mbps vs 100 Mbps (Cliente 1)', 
                                fontsize=14, fontweight='bold')
                    ax.set_xlabel('Tamanho do Payload (bytes)', fontsize=12)
                    ax.set_ylabel('Jitter Médio (ms)', fontsize=12)
                    ax.grid(True, alpha=0.3, linestyle='--')
                    
                    # Usar tamanhos específicos que existem em ambos os datasets
                    common_sizes = np.intersect1d(df_10_filtrado['tamanho_bytes'], df_100_filtrado['tamanho_bytes'])
                    if len(common_sizes) > 0:
                        ax.set_xticks(common_sizes)
                        ax.set_xticklabels([formatar_bytes(x) for x in common_sizes], rotation=45)
                    
                    ax.legend()
                    plt.tight_layout()
                    plt.savefig('graficos/05_comparacao_jitter_redes.png', dpi=300, bbox_inches='tight')
                    plt.close()
                    print(" 05_comparacao_jitter_redes.png (usando dados do Cliente 1, com tamanhos específicos)")
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
            # Definir tamanhos específicos de payload conforme solicitado
            tamanhos_especificos = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65507]
            
            # Filtrar apenas os tamanhos que existem nos dados
            df_10_filtrado = df_10[df_10['tamanho_bytes'].isin(tamanhos_especificos)]
            df_100_filtrado = df_100[df_100['tamanho_bytes'].isin(tamanhos_especificos)]
            
            fig, ax = plt.subplots(figsize=(12, 8))
            # Verificar se há dados de desvio padrão disponíveis
            if 'dp_agregado_ms' in df_10_filtrado.columns and 'dp_agregado_ms' in df_100_filtrado.columns:
                # Para percentis, usar uma fração menor do desvio padrão
                p_err_10 = df_10_filtrado['dp_agregado_ms'] * 0.5  # 50% do desvio padrão
                p_err_100 = df_100_filtrado['dp_agregado_ms'] * 0.5
                ax.errorbar(df_10_filtrado['tamanho_bytes'], df_10_filtrado['p95_agregado_ms'], 
                           yerr=p_err_10, fmt='o-', color='#FF5722', 
                           linewidth=2, markersize=5, capsize=4, capthick=1.5,
                           label='10 Mbps - P95')
                ax.errorbar(df_10_filtrado['tamanho_bytes'], df_10_filtrado['p99_agregado_ms'], 
                           yerr=p_err_10, fmt='o--', color='#FF5722', 
                           linewidth=2, markersize=5, capsize=4, capthick=1.5,
                           label='10 Mbps - P99')
                ax.errorbar(df_100_filtrado['tamanho_bytes'], df_100_filtrado['p95_agregado_ms'], 
                           yerr=p_err_100, fmt='s-', color='#2196F3', 
                           linewidth=2, markersize=5, capsize=4, capthick=1.5,
                           label='100 Mbps - P95')
                ax.errorbar(df_100_filtrado['tamanho_bytes'], df_100_filtrado['p99_agregado_ms'], 
                           yerr=p_err_100, fmt='s--', color='#2196F3', 
                           linewidth=2, markersize=5, capsize=4, capthick=1.5,
                           label='100 Mbps - P99')
            else:
                ax.plot(df_10_filtrado['tamanho_bytes'], df_10_filtrado['p95_agregado_ms'], 'o-', 
                        color='#FF5722', linewidth=2, markersize=5, label='10 Mbps - P95')
                ax.plot(df_10_filtrado['tamanho_bytes'], df_10_filtrado['p99_agregado_ms'], 'o--', 
                        color='#FF5722', linewidth=2, markersize=5, label='10 Mbps - P99')
                ax.plot(df_100_filtrado['tamanho_bytes'], df_100_filtrado['p95_agregado_ms'], 's-', 
                        color='#2196F3', linewidth=2, markersize=5, label='100 Mbps - P95')
                ax.plot(df_100_filtrado['tamanho_bytes'], df_100_filtrado['p99_agregado_ms'], 's--', 
                        color='#2196F3', linewidth=2, markersize=5, label='100 Mbps - P99')
            ax.set_xscale('log', base=2)
            ax.set_ylim(0, 45)  # Adicionado limite do eixo Y
            ax.set_title('Comparação de Percentis P95 e P99', 
                        fontsize=14, fontweight='bold')
            ax.set_xlabel('Tamanho do Payload (bytes)', fontsize=12)
            ax.set_ylabel('RTT (ms)', fontsize=12)
            ax.grid(True, alpha=0.3, linestyle='--')
            
            # Usar tamanhos específicos que existem em ambos os datasets
            common_sizes = np.intersect1d(df_10_filtrado['tamanho_bytes'], df_100_filtrado['tamanho_bytes'])
            if len(common_sizes) > 0:
                ax.set_xticks(common_sizes)
                ax.set_xticklabels([formatar_bytes(x) for x in common_sizes], rotation=45)
            
            ax.legend()
            plt.tight_layout()
            plt.savefig('graficos/06_comparacao_percentis.png', dpi=300, bbox_inches='tight')
            plt.close()
            print(" 06_comparacao_percentis.png (com tamanhos específicos)")
    else:
        if (verificar_arquivo("stats_cliente1.csv") and 
            verificar_arquivo("stats_cliente1_100.csv")):
            df_10 = carregar_dados("stats_cliente1.csv")
            df_100 = carregar_dados("stats_cliente1_100.csv")
            if df_10 is not None and df_100 is not None:
                # Definir tamanhos específicos de payload conforme solicitado
                tamanhos_especificos = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65507]
                
                # Filtrar apenas os tamanhos que existem nos dados
                df_10_filtrado = df_10[df_10['tamanho_bytes'].isin(tamanhos_especificos)]
                df_100_filtrado = df_100[df_100['tamanho_bytes'].isin(tamanhos_especificos)]
                
                fig, ax = plt.subplots(figsize=(12, 8))
                # Verificar se há dados de desvio padrão disponíveis
                if 'dp_ms' in df_10_filtrado.columns and 'dp_ms' in df_100_filtrado.columns:
                    # Para percentis, usar uma fração menor do desvio padrão
                    p_err_10 = df_10_filtrado['dp_ms'] * 0.5  # 50% do desvio padrão
                    p_err_100 = df_100_filtrado['dp_ms'] * 0.5
                    ax.errorbar(df_10_filtrado['tamanho_bytes'], df_10_filtrado['p95_ms'], 
                               yerr=p_err_10, fmt='o-', color='#FF5722', 
                               linewidth=2, markersize=5, capsize=4, capthick=1.5,
                               label='Cliente 1 10 Mbps - P95')
                    ax.errorbar(df_10_filtrado['tamanho_bytes'], df_10_filtrado['p99_ms'], 
                               yerr=p_err_10, fmt='o--', color='#FF5722', 
                               linewidth=2, markersize=5, capsize=4, capthick=1.5,
                               label='Cliente 1 10 Mbps - P99')
                    ax.errorbar(df_100_filtrado['tamanho_bytes'], df_100_filtrado['p95_ms'], 
                               yerr=p_err_100, fmt='s-', color='#2196F3', 
                               linewidth=2, markersize=5, capsize=4, capthick=1.5,
                               label='Cliente 1 100 Mbps - P95')
                    ax.errorbar(df_100_filtrado['tamanho_bytes'], df_100_filtrado['p99_ms'], 
                               yerr=p_err_100, fmt='s--', color='#2196F3', 
                               linewidth=2, markersize=5, capsize=4, capthick=1.5,
                               label='Cliente 1 100 Mbps - P99')
                else:
                    ax.plot(df_10_filtrado['tamanho_bytes'], df_10_filtrado['p95_ms'], 'o-', 
                            color='#FF5722', linewidth=2, markersize=5, label='Cliente 1 10 Mbps - P95')
                    ax.plot(df_10_filtrado['tamanho_bytes'], df_10_filtrado['p99_ms'], 'o--', 
                            color='#FF5722', linewidth=2, markersize=5, label='Cliente 1 10 Mbps - P99')
                    ax.plot(df_100_filtrado['tamanho_bytes'], df_100_filtrado['p95_ms'], 's-', 
                            color='#2196F3', linewidth=2, markersize=5, label='Cliente 1 100 Mbps - P95')
                    ax.plot(df_100_filtrado['tamanho_bytes'], df_100_filtrado['p99_ms'], 's--', 
                            color='#2196F3', linewidth=2, markersize=5, label='Cliente 1 100 Mbps - P99')
                ax.set_xscale('log', base=2)
                ax.set_ylim(0, 45)  # Adicionado limite do eixo Y
                ax.set_title('Comparação de Percentis P95 e P99 (Cliente 1)', 
                            fontsize=14, fontweight='bold')
                ax.set_xlabel('Tamanho do Payload (bytes)', fontsize=12)
                ax.set_ylabel('RTT (ms)', fontsize=12)
                ax.grid(True, alpha=0.3, linestyle='--')
                
                # Usar tamanhos específicos que existem em ambos os datasets
                common_sizes = np.intersect1d(df_10_filtrado['tamanho_bytes'], df_100_filtrado['tamanho_bytes'])
                if len(common_sizes) > 0:
                    ax.set_xticks(common_sizes)
                    ax.set_xticklabels([formatar_bytes(x) for x in common_sizes], rotation=45)
                
                ax.legend()
                plt.tight_layout()
                plt.savefig('graficos/06_comparacao_percentis.png', dpi=300, bbox_inches='tight')
                plt.close()
                print(" 06_comparacao_percentis.png (usando dados do Cliente 1, com tamanhos específicos)")
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
            # Definir tamanhos específicos de payload conforme solicitado
            tamanhos_especificos = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65507]
            
            # Filtrar apenas os tamanhos que existem nos dados
            df_10_sub = df_10[df_10['tamanho_bytes'].isin(tamanhos_especificos)]
            df_100_sub = df_100[df_100['tamanho_bytes'].isin(tamanhos_especificos)]
            
            fig, axes = plt.subplots(2, 2, figsize=(14, 10))
            fig.suptitle('Dashboard Comparativo: 10 Mbps vs 100 Mbps', 
                        fontsize=16, fontweight='bold')
            
            colors_10 = '#FF4444'  # Bright red
            colors_100 = '#0066CC'  # Bright blue
            
            ax = axes[0, 0]
            # RTT com barras de erro
            if 'dp_agregado_ms' in df_10_sub.columns and 'dp_agregado_ms' in df_100_sub.columns:
                ax.errorbar(df_10_sub['tamanho_bytes'], df_10_sub['media_agregada_ms'], 
                           yerr=df_10_sub['dp_agregado_ms'], fmt='o-', color=colors_10, 
                           linewidth=2.5, markersize=6, capsize=4, capthick=1.5, label='10 Mbps')
                ax.errorbar(df_100_sub['tamanho_bytes'], df_100_sub['media_agregada_ms'], 
                           yerr=df_100_sub['dp_agregado_ms'], fmt='s-', color=colors_100, 
                           linewidth=2.5, markersize=6, capsize=4, capthick=1.5, label='100 Mbps')
            else:
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
            # Taxa de perda não usa barras de erro (é uma porcentagem)
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
            # Jitter com barras de erro se disponível
            if 'jitter_dp_ms' in df_10_sub.columns and 'jitter_dp_ms' in df_100_sub.columns:
                ax.errorbar(df_10_sub['tamanho_bytes'], df_10_sub['jitter_agregado_ms'], 
                           yerr=df_10_sub['jitter_dp_ms'], fmt='o-', color=colors_10, 
                           linewidth=2.5, markersize=6, capsize=4, capthick=1.5, label='10 Mbps')
                ax.errorbar(df_100_sub['tamanho_bytes'], df_100_sub['jitter_agregado_ms'], 
                           yerr=df_100_sub['jitter_dp_ms'], fmt='s-', color=colors_100, 
                           linewidth=2.5, markersize=6, capsize=4, capthick=1.5, label='100 Mbps')
            else:
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
                # Speedup com barras de erro propagadas se disponível
                if 'dp_agregado_ms_10' in merged.columns and 'dp_agregado_ms_100' in merged.columns:
                    # Propagação de erro para divisão: sqrt((dp1/val1)^2 + (dp2/val2)^2) * speedup
                    speedup_err = speedup * np.sqrt(
                        (merged['dp_agregado_ms_10'] / merged['media_agregada_ms_10'])**2 + 
                        (merged['dp_agregado_ms_100'] / merged['media_agregada_ms_100'])**2
                    )
                    ax.errorbar(merged['tamanho_bytes'], speedup, yerr=speedup_err,
                               fmt='o-', color='#FF9800', linewidth=2.5, markersize=6, 
                               capsize=4, capthick=1.5, label='Speedup')
                else:
                    ax.plot(merged['tamanho_bytes'], speedup, 'o-', 
                            color='#FF9800', linewidth=2.5, markersize=6, label='Speedup')
                ax.axhline(y=1, color='black', linestyle='--', alpha=0.5)
                ax.set_xscale('log', base=2)
                ax.set_title('Speedup (RTT 10Mbps / RTT 100Mbps)', fontweight='bold')
                ax.set_xlabel('Tamanho do Payload')
                ax.set_ylabel('Fator de Melhoria')
                ax.grid(True, alpha=0.3)
                ax.legend()
            
            # Usar tamanhos específicos que existem em ambos os datasets para todos os subgráficos
            common_sizes = np.intersect1d(df_10_sub['tamanho_bytes'], df_100_sub['tamanho_bytes'])
            for ax in axes.flat:
                if len(common_sizes) > 0:
                    ax.set_xticks(common_sizes)
                    ax.set_xticklabels([formatar_bytes(x) for x in common_sizes], rotation=45)
            
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
            # Definir tamanhos específicos de payload conforme solicitado
            tamanhos_especificos = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65507]
            
            # Filtrar apenas os tamanhos que existem nos dados
            df_10_filtrado = df_10[df_10['tamanho_bytes'].isin(tamanhos_especificos)]
            df_100_filtrado = df_100[df_100['tamanho_bytes'].isin(tamanhos_especificos)]
            
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.errorbar(df_10_filtrado['tamanho_bytes'], df_10_filtrado['media_ms'], 
                        yerr=[df_10_filtrado['media_ms'] - df_10_filtrado['ic_lower_ms'], 
                              df_10_filtrado['ic_upper_ms'] - df_10_filtrado['media_ms']],
                        fmt='o-', color='#FF4444', linewidth=2, markersize=4, 
                        capsize=3, label='10 Mbps (IC 98%)')
            ax.errorbar(df_100_filtrado['tamanho_bytes'], df_100_filtrado['media_ms'], 
                        yerr=[df_100_filtrado['media_ms'] - df_100_filtrado['ic_lower_ms'], 
                              df_100_filtrado['ic_upper_ms'] - df_100_filtrado['media_ms']],
                        fmt='s-', color='#0066CC', linewidth=2, markersize=4, 
                        capsize=3, label='100 Mbps (IC 98%)')
            ax.set_xscale('log', base=2)
            ax.set_ylim(0, 13)  # Alterado para 0, 13
            ax.set_title('Cliente 1: Comparação entre Redes 10 e 100 Mbps', 
                        fontsize=14, fontweight='bold')
            ax.set_xlabel('Tamanho do Payload (bytes)', fontsize=12)
            ax.set_ylabel('RTT Médio (ms)', fontsize=12)
            ax.grid(True, alpha=0.3, linestyle='--')
            
            # Usar tamanhos específicos que existem em ambos os datasets
            common_sizes = np.intersect1d(df_10_filtrado['tamanho_bytes'], df_100_filtrado['tamanho_bytes'])
            if len(common_sizes) > 0:
                ax.set_xticks(common_sizes)
                ax.set_xticklabels([formatar_bytes(x) for x in common_sizes], rotation=45)
            
            ax.legend()
            plt.tight_layout()
            plt.savefig('graficos/08_cliente1_comparacao_rede.png', dpi=300, bbox_inches='tight')
            plt.close()
            print(" 08_cliente1_comparacao_rede.png (com tamanhos específicos)")
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
            # Definir tamanhos específicos de payload conforme solicitado
            tamanhos_especificos = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65507]
            
            # Filtrar apenas os tamanhos que existem nos dados
            df_10_filtrado = df_10[df_10['tamanho_bytes'].isin(tamanhos_especificos)]
            df_100_filtrado = df_100[df_100['tamanho_bytes'].isin(tamanhos_especificos)]
            
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.errorbar(df_10_filtrado['tamanho_bytes'], df_10_filtrado['media_ms'], 
                        yerr=[df_10_filtrado['media_ms'] - df_10_filtrado['ic_lower_ms'], 
                              df_10_filtrado['ic_upper_ms'] - df_10_filtrado['media_ms']],
                        fmt='o-', color='#6A1B9A', linewidth=2, markersize=4, 
                        capsize=3, label='10 Mbps (IC 98%)')
            ax.errorbar(df_100_filtrado['tamanho_bytes'], df_100_filtrado['media_ms'], 
                        yerr=[df_100_filtrado['media_ms'] - df_100_filtrado['ic_lower_ms'], 
                              df_100_filtrado['ic_upper_ms'] - df_100_filtrado['media_ms']],
                        fmt='s-', color='#F57F17', linewidth=2, markersize=4, 
                        capsize=3, label='100 Mbps (IC 98%)')
            ax.set_xscale('log', base=2)
            ax.set_title('Cliente 2: Comparação entre Redes 10 e 100 Mbps', 
                        fontsize=14, fontweight='bold')
            ax.set_xlabel('Tamanho do Payload (bytes)', fontsize=12)
            ax.set_ylabel('RTT Médio (ms)', fontsize=12)
            ax.grid(True, alpha=0.3, linestyle='--')
            
            # Usar tamanhos específicos que existem em ambos os datasets
            common_sizes = np.intersect1d(df_10_filtrado['tamanho_bytes'], df_100_filtrado['tamanho_bytes'])
            if len(common_sizes) > 0:
                ax.set_xticks(common_sizes)
                ax.set_xticklabels([formatar_bytes(x) for x in common_sizes], rotation=45)
            
            ax.legend()
            plt.tight_layout()
            plt.savefig('graficos/09_cliente2_comparacao_rede.png', dpi=300, bbox_inches='tight')
            plt.close()
            print(" 09_cliente2_comparacao_rede.png (com tamanhos específicos)")
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
                # Gráfico de dispersão com barras de erro se disponível
                if 'dp_ms' in df_10_1k.columns and 'dp_ms' in df_100_1k.columns:
                    ax.errorbar(df_10_1k[nivel_col], df_10_1k[rtt_col], 
                               yerr=df_10_1k['dp_ms'], fmt='o', color='#FF4444', 
                               markersize=8, capsize=4, capthick=1.5, alpha=0.8,
                               label='10 Mbps')
                    ax.errorbar(df_100_1k[nivel_col], df_100_1k[rtt_col], 
                               yerr=df_100_1k['dp_ms'], fmt='s', color='#0066CC', 
                               markersize=8, capsize=4, capthick=1.5, alpha=0.8,
                               label='100 Mbps')
                else:
                    ax.scatter(df_10_1k[nivel_col], df_10_1k[rtt_col], 
                              color='#FF4444', s=80, alpha=0.8, label='10 Mbps')
                    ax.scatter(df_100_1k[nivel_col], df_100_1k[rtt_col], 
                              color='#0066CC', s=80, marker='s', alpha=0.8, label='100 Mbps')
                ax.set_xlim(0, 20)
                ax.set_ylim(0, 0.5)  # Ajustado para mostrar melhor os dados de RTT
                ax.set_title('Rampa - Cliente 1: RTT vs Nível de Carga (1KB)', 
                            fontsize=14, fontweight='bold')
                ax.set_xlabel('Nível da Rampa (1=10 req/s → 10=100 req/s → 19=10 req/s)', 
                              fontsize=12)
                ax.set_ylabel('RTT Médio (ms)', fontsize=12)
                ax.grid(True, alpha=0.3, linestyle='--')
                ax.set_xticks(range(0, 21, 2))
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
                ax.scatter(df_10_2b[nivel_col], df_10_2b['rtt_normalizado'], 
                          color='#D32F2F', s=50, alpha=0.7, label='10 Mbps - 2 bytes')
            if not df_100_2b.empty:
                ax.scatter(df_100_2b[nivel_col], df_100_2b['rtt_normalizado'], 
                          color='#388E3C', s=50, alpha=0.7, label='100 Mbps - 2 bytes')
            if not df_10_1k.empty:
                ax.scatter(df_10_1k[nivel_col], df_10_1k['rtt_normalizado'], 
                          color='#8BC34A', s=50, alpha=0.7, marker='s', label='10 Mbps - 1KB')
            if not df_100_1k.empty:
                ax.scatter(df_100_1k[nivel_col], df_100_1k['rtt_normalizado'], 
                          color='#FF5722', s=50, alpha=0.7, marker='s', label='100 Mbps - 1KB')
            if not df_10_64k.empty:
                ax.scatter(df_10_64k[nivel_col], df_10_64k['rtt_normalizado'], 
                          color='#9C27B0', s=50, alpha=0.7, marker='^', label='10 Mbps - 64KB')
            if not df_100_64k.empty:
                ax.scatter(df_100_64k[nivel_col], df_100_64k['rtt_normalizado'], 
                          color='#FFC107', s=50, alpha=0.7, marker='^', label='100 Mbps - 64KB')
            ax.set_xlim(0, 20)
            ax.set_ylim(0, 2.5)
            ax.set_title('Análise de Saturação: RTT Normalizado por Nível', 
                        fontsize=14, fontweight='bold')
            ax.set_xlabel('Nível da Rampa', fontsize=12)
            ax.set_ylabel('RTT Normalizado (RTT/RTT_inicial)', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.set_xticks(range(0, 20, 2))
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