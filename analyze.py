import csv
import glob
import os
import statistics
from math import sqrt

Z_98 = 2.3263

EXPECTED_MEASURES = 1000
EXPECTED_MEASURES_PER_LEVEL = 100

def read_raw_data(filepath):
    """
    Lê raw_data_clienteX.csv ou raw_data_clienteX_100.csv e retorna dicionário:
      { tamanho_bytes: [rtt1, rtt2, ...] }
    Descartamos rtt < 0 (timeouts).
    """
    data = {}
    total_per_size = {}
    
    if not os.path.exists(filepath):
        print(f"[WARN] Arquivo não encontrado: {filepath}")
        return data, total_per_size
    
    try:
        line_count = 0
        valid_count = 0
        invalid_count = 0
        
        with open(filepath, newline="") as f:
            reader = csv.DictReader(f)
            
            if reader.fieldnames:
                print(f"[DEBUG] Colunas encontradas: {reader.fieldnames}")
            
            for row in reader:
                line_count += 1
                
                if "tamanho_bytes" not in row or "rtt_ms" not in row:
                    invalid_count += 1
                    continue
                    
                try:
                    size = int(row["tamanho_bytes"])
                except (ValueError, TypeError):
                    invalid_count += 1
                    continue
                    
                total_per_size[size] = total_per_size.get(size, 0) + 1
                
                rtt_value = row.get("rtt_ms")
                if rtt_value is None or rtt_value == "":
                    invalid_count += 1
                    continue
                    
                try:
                    rtt = float(rtt_value)
                except (ValueError, TypeError):
                    invalid_count += 1
                    continue
                    
                if rtt < 0:
                    continue
                    
                data.setdefault(size, []).append(rtt)
                valid_count += 1
        
        print(f"[INFO] {filepath}: {line_count} linhas lidas, {valid_count} RTTs válidos, {invalid_count} linhas inválidas")
        
    except Exception as e:
        print(f"[ERROR] Erro ao processar {filepath}: {e}")
    
    return data, total_per_size

def read_ramp_data(filepath):
    """
    Lê ramp_data_clienteX.csv ou ramp_data_clienteX_100.csv e retorna dicionário:
      { (tamanho_bytes, nivel): [rtt1, rtt2, ...] }
    """
    data = {}
    total_per_key = {}
    
    if not os.path.exists(filepath):
        print(f"[WARN] Arquivo não encontrado: {filepath}")
        return data, total_per_key
    
    try:
        with open(filepath, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if "tamanho_bytes" not in row or "nivel" not in row or "rtt_ms" not in row:
                    continue
                    
                try:
                    size = int(row["tamanho_bytes"])
                    nivel = int(row["nivel"])
                except (ValueError, TypeError):
                    continue
                    
                key = (size, nivel)
                total_per_key[key] = total_per_key.get(key, 0) + 1
                
                rtt_value = row.get("rtt_ms")
                if rtt_value is None or rtt_value == "":
                    continue
                    
                try:
                    rtt = float(rtt_value)
                except (ValueError, TypeError):
                    continue
                    
                if rtt < 0:
                    continue
                    
                data.setdefault(key, []).append(rtt)
    except Exception as e:
        print(f"[ERROR] Erro ao processar {filepath}: {e}")
    
    return data, total_per_key

def detect_outliers(rtts):
    """Detecta outliers usando método IQR."""
    if len(rtts) < 4:
        return 0, []
    
    sorted_rtts = sorted(rtts)
    q1_idx = len(sorted_rtts) // 4
    q3_idx = 3 * len(sorted_rtts) // 4
    
    q1 = sorted_rtts[q1_idx]
    q3 = sorted_rtts[q3_idx]
    iqr = q3 - q1
    
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    
    outliers = [x for x in rtts if x < lower_bound or x > upper_bound]
    return len(outliers), outliers

def compute_percentile(sorted_data, percentile):
    """Calcula percentil de uma lista ordenada."""
    if not sorted_data:
        return float("nan")
    
    k = (len(sorted_data) - 1) * percentile / 100
    f = int(k)
    c = k - f
    
    if f + 1 < len(sorted_data):
        return sorted_data[f] + c * (sorted_data[f + 1] - sorted_data[f])
    else:
        return sorted_data[f]

def compute_stats(rtts, total_attempts=None):
    """
    Calcula estatísticas completas incluindo média, mediana, percentis, etc.
    """
    n = len(rtts)
    if n == 0:
        return (0, float("nan"), float("nan"), float("nan"),
                float("nan"), float("nan"), float("nan"),
                float("nan"), float("nan"), float("nan"),
                float("nan"), 100.0, 0)

    rtts_sorted = sorted(rtts)
    media = statistics.mean(rtts_sorted)
    mediana = statistics.median(rtts_sorted)
    dp = statistics.stdev(rtts_sorted) if n > 1 else 0.0
    min_rtt = rtts_sorted[0]
    max_rtt = rtts_sorted[-1]

    if n > 1:
        diffs = [abs(rtts_sorted[i] - rtts_sorted[i - 1]) for i in range(1, n)]
        jitter = statistics.mean(diffs)
    else:
        jitter = 0.0

    ic_half = Z_98 * (dp / sqrt(n)) if n > 1 else 0.0
    ic_low = media - ic_half
    ic_up = media + ic_half
    
    p95 = compute_percentile(rtts_sorted, 95)
    p99 = compute_percentile(rtts_sorted, 99)
    
    if total_attempts:
        taxa_perda = ((total_attempts - n) / total_attempts) * 100
    else:
        taxa_perda = 0.0
    
    num_outliers, _ = detect_outliers(rtts)
    
    return (n, media, mediana, dp, jitter, ic_low, ic_up, 
            p95, p99, min_rtt, max_rtt, taxa_perda, num_outliers)

def process_raw_files_by_network(network_speed):
    """
    Processa arquivos raw_data para uma velocidade de rede específica.
    network_speed: "10" ou "100"
    """
    suffix = "_100" if network_speed == "100" else ""
    pattern = f"raw_data_cliente*{suffix}.csv"
    raw_files = glob.glob(pattern)
    
    if not raw_files:
        print(f"[INFO] Nenhum arquivo {pattern} encontrado para rede de {network_speed} Mbps.")
        return False
    
    print(f"\n[INFO] Processando {len(raw_files)} arquivo(s) para rede de {network_speed} Mbps...")
    
    for raw_path in sorted(raw_files):
        print(f"\n[ANALYZE] Processando: {raw_path}")
        
        base = os.path.basename(raw_path).replace("raw_data_", "").replace(".csv", "")
        out_path = f"stats_{base}.csv"

        data, total_per_size = read_raw_data(raw_path)
        
        if not data:
            print(f"[WARN] Nenhum dado válido encontrado em {raw_path}")
            continue
            
        sizes = sorted(data.keys())
        print(f"[INFO] Encontrados {len(sizes)} tamanhos diferentes com dados válidos")

        try:
            with open(out_path, "w", newline="") as fout:
                writer = csv.writer(fout)
                writer.writerow([
                    "tamanho_bytes", "n_validos", "media_ms",
                    "mediana_ms", "dp_ms", "jitter_ms",
                    "ic_lower_ms", "ic_upper_ms", "p95_ms", "p99_ms",
                    "min_ms", "max_ms", "taxa_perda_%", "num_outliers"
                ])
                
                for size in sizes:
                    rtts = data[size]
                    total_attempts = total_per_size.get(size, EXPECTED_MEASURES)
                    stats = compute_stats(rtts, total_attempts)
                    
                    writer.writerow([
                        size,
                        stats[0], f"{stats[1]:.5f}", f"{stats[2]:.5f}",
                        f"{stats[3]:.5f}", f"{stats[4]:.5f}", f"{stats[5]:.5f}",
                        f"{stats[6]:.5f}", f"{stats[7]:.5f}", f"{stats[8]:.5f}",
                        f"{stats[9]:.5f}", f"{stats[10]:.5f}", f"{stats[11]:.2f}",
                        stats[12]
                    ])
                
                print(f"[SUCCESS] Estatísticas gravadas em {out_path}")
                
        except Exception as e:
            print(f"[ERROR] Erro ao escrever {out_path}: {e}")
    
    return True

def process_ramp_files_by_network(network_speed):
    """
    Processa arquivos ramp_data para uma velocidade de rede específica.
    """
    suffix = "_100" if network_speed == "100" else ""
    pattern = f"ramp_data_cliente*{suffix}.csv"
    ramp_files = glob.glob(pattern)
    
    if not ramp_files:
        print(f"[INFO] Nenhum arquivo {pattern} encontrado para rede de {network_speed} Mbps.")
        return False
    
    print(f"\n[INFO] Processando {len(ramp_files)} arquivo(s) de rampa para rede de {network_speed} Mbps...")
    
    for ramp_path in sorted(ramp_files):
        base = os.path.basename(ramp_path).replace("ramp_data_", "").replace(".csv", "")
        out_path = f"stats_ramp_{base}.csv"

        data, total_per_key = read_ramp_data(ramp_path)
        
        if not data:
            print(f"[WARN] Nenhum dado válido encontrado em {ramp_path}")
            continue
            
        keys = sorted(data.keys(), key=lambda x: (x[0], x[1]))

        with open(out_path, "w", newline="") as fout:
            writer = csv.writer(fout)
            writer.writerow([
                "tamanho_bytes", "nivel", "n_validos",
                "media_ms", "mediana_ms", "dp_ms",
                "jitter_ms", "ic_lower_ms", "ic_upper_ms",
                "p95_ms", "p99_ms", "min_ms", "max_ms",
                "taxa_perda_%", "num_outliers"
            ])
            
            for (size, nivel) in keys:
                rtts = data[(size, nivel)]
                total_attempts = total_per_key.get((size, nivel), EXPECTED_MEASURES_PER_LEVEL)
                stats = compute_stats(rtts, total_attempts)
                
                writer.writerow([
                    size, nivel,
                    stats[0], f"{stats[1]:.5f}", f"{stats[2]:.5f}",
                    f"{stats[3]:.5f}", f"{stats[4]:.5f}", f"{stats[5]:.5f}",
                    f"{stats[6]:.5f}", f"{stats[7]:.5f}", f"{stats[8]:.5f}",
                    f"{stats[9]:.5f}", f"{stats[10]:.5f}", f"{stats[11]:.2f}",
                    stats[12]
                ])

        print(f"[SUCCESS] Estatísticas de rampa gravadas em {out_path}")
    
    return True

def aggregate_clients_by_network(network_speed):
    """
    Agrega dados de ambos os clientes para uma rede específica.
    """
    suffix = "_100" if network_speed == "100" else ""
    stats_files = glob.glob(f"stats_cliente*{suffix}.csv")
    
    if len(stats_files) != 2:
        return False
    
    out_path = f"stats_network_{network_speed}mbps.csv"
    
    all_data = {}
    
    for stats_file in stats_files:
        with open(stats_file, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                size = int(row["tamanho_bytes"])
                if size not in all_data:
                    all_data[size] = {
                        'media': [], 'mediana': [], 'p95': [], 'p99': [],
                        'jitter': [], 'taxa_perda': [], 'n_total': 0
                    }
                
                all_data[size]['media'].append(float(row["media_ms"]))
                all_data[size]['mediana'].append(float(row["mediana_ms"]))
                all_data[size]['p95'].append(float(row["p95_ms"]))
                all_data[size]['p99'].append(float(row["p99_ms"]))
                all_data[size]['jitter'].append(float(row["jitter_ms"]))
                all_data[size]['taxa_perda'].append(float(row["taxa_perda_%"]))
                all_data[size]['n_total'] += int(row["n_validos"])
    
    with open(out_path, "w", newline="") as fout:
        writer = csv.writer(fout)
        writer.writerow([
            "tamanho_bytes", "media_agregada_ms", "mediana_agregada_ms",
            "p95_agregado_ms", "p99_agregado_ms", "jitter_agregado_ms",
            "taxa_perda_agregada_%", "n_total_amostras"
        ])
        
        for size in sorted(all_data.keys()):
            writer.writerow([
                size,
                f"{statistics.mean(all_data[size]['media']):.5f}",
                f"{statistics.mean(all_data[size]['mediana']):.5f}",
                f"{statistics.mean(all_data[size]['p95']):.5f}",
                f"{statistics.mean(all_data[size]['p99']):.5f}",
                f"{statistics.mean(all_data[size]['jitter']):.5f}",
                f"{statistics.mean(all_data[size]['taxa_perda']):.2f}",
                all_data[size]['n_total']
            ])
    
    print(f"[SUCCESS] Dados agregados da rede {network_speed} Mbps salvos em {out_path}")
    return True

def generate_summary_report():
    """
    Gera relatório resumido comparando redes de 10 e 100 Mbps.
    """
    print("\n" + "="*60)
    print("RESUMO DA ANÁLISE DE DESEMPENHO UDP")
    print("="*60)
    
    print("\n### RELATÓRIO DE PERDA DE PACOTES ###")
    
    for pattern in ["raw_data_cliente*.csv", "raw_data_cliente*_100.csv"]:
        for filepath in sorted(glob.glob(pattern)):
            if os.path.exists(filepath):
                print(f"\n--- {filepath} ---")
                
                total_registros = 0
                registros_validos = 0
                registros_timeout = 0
                
                with open(filepath, newline="") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        total_registros += 1
                        try:
                            rtt = float(row.get("rtt_ms", 0))
                            if rtt >= 0:
                                registros_validos += 1
                            else:
                                registros_timeout += 1
                        except:
                            registros_timeout += 1
                
                if total_registros > 0:
                    taxa_perda = (registros_timeout / total_registros) * 100
                    taxa_sucesso = (registros_validos / total_registros) * 100
                    
                    print(f"Total de registros: {total_registros}")
                    print(f"Registros válidos: {registros_validos} ({taxa_sucesso:.2f}%)")
                    print(f"Timeouts/Perdas: {registros_timeout} ({taxa_perda:.2f}%)")
                else:
                    print("Arquivo vazio ou sem dados válidos")
    
    print("\n### RELATÓRIO DE RAMPA ###")
    for pattern in ["ramp_data_cliente*.csv", "ramp_data_cliente*_100.csv"]:
        for filepath in sorted(glob.glob(pattern)):
            if os.path.exists(filepath):
                print(f"\n--- {filepath} ---")
                
                total_registros = 0
                registros_validos = 0
                registros_timeout = 0
                
                with open(filepath, newline="") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        total_registros += 1
                        try:
                            rtt = float(row.get("rtt_ms", 0))
                            if rtt >= 0:
                                registros_validos += 1
                            else:
                                registros_timeout += 1
                        except:
                            registros_timeout += 1
                
                if total_registros > 0:
                    taxa_perda = (registros_timeout / total_registros) * 100
                    taxa_sucesso = (registros_validos / total_registros) * 100
                    
                    print(f"Total de registros: {total_registros}")
                    print(f"Registros válidos: {registros_validos} ({taxa_sucesso:.2f}%)")
                    print(f"Timeouts/Perdas: {registros_timeout} ({taxa_perda:.2f}%)")
                else:
                    print("Arquivo vazio ou sem dados válidos")
    
    print("\n### ANÁLISE AGREGADA POR REDE ###")
    
    if os.path.exists("stats_network_10mbps.csv"):
        print("\n--- REDE DE 10 Mbps ---")
        with open("stats_network_10mbps.csv", newline="") as f:
            reader = list(csv.DictReader(f))
            if reader:
                avg_rtt = statistics.mean(float(r["media_agregada_ms"]) for r in reader)
                avg_loss = statistics.mean(float(r["taxa_perda_agregada_%"]) for r in reader)
                max_loss = max(float(r["taxa_perda_agregada_%"]) for r in reader)
                min_loss = min(float(r["taxa_perda_agregada_%"]) for r in reader)
                
                print(f"RTT médio geral: {avg_rtt:.3f} ms")
                print(f"Taxa de perda média: {avg_loss:.2f}%")
                print(f"Taxa de perda máxima: {max_loss:.2f}%")
                print(f"Taxa de perda mínima: {min_loss:.2f}%")
                
                max_loss_size = max(reader, key=lambda r: float(r["taxa_perda_agregada_%"]))
                print(f"Tamanho com maior perda: {max_loss_size['tamanho_bytes']} bytes ({float(max_loss_size['taxa_perda_agregada_%']):.2f}%)")
    
    if os.path.exists("stats_network_100mbps.csv"):
        print("\n--- REDE DE 100 Mbps ---")
        with open("stats_network_100mbps.csv", newline="") as f:
            reader = list(csv.DictReader(f))
            if reader:
                avg_rtt = statistics.mean(float(r["media_agregada_ms"]) for r in reader)
                avg_loss = statistics.mean(float(r["taxa_perda_agregada_%"]) for r in reader)
                max_loss = max(float(r["taxa_perda_agregada_%"]) for r in reader)
                min_loss = min(float(r["taxa_perda_agregada_%"]) for r in reader)
                
                print(f"RTT médio geral: {avg_rtt:.3f} ms")
                print(f"Taxa de perda média: {avg_loss:.2f}%")
                print(f"Taxa de perda máxima: {max_loss:.2f}%")
                print(f"Taxa de perda mínima: {min_loss:.2f}%")
                
                max_loss_size = max(reader, key=lambda r: float(r["taxa_perda_agregada_%"]))
                print(f"Tamanho com maior perda: {max_loss_size['tamanho_bytes']} bytes ({float(max_loss_size['taxa_perda_agregada_%']):.2f}%)")
    
    print("\n" + "="*60)

def main():
    print("[ANALYZE] Iniciando processamento dos dados...")
    print("[ANALYZE] Analisando estrutura de arquivos...\n")
    
    has_10mbps = process_raw_files_by_network("10")
    if has_10mbps:
        aggregate_clients_by_network("10")
    
    has_10mbps_ramp = process_ramp_files_by_network("10")
    
    has_100mbps = process_raw_files_by_network("100")
    if has_100mbps:
        aggregate_clients_by_network("100")
    
    has_100mbps_ramp = process_ramp_files_by_network("100")
    
    if has_10mbps or has_100mbps:
        generate_summary_report()
    else:
        print("[ERROR] Nenhum arquivo de dados encontrado!")
        print("[ERROR] Certifique-se de que existem arquivos:")
        print("        - raw_data_cliente[1-2].csv (rede 10 Mbps)")
        print("        - raw_data_cliente[1-2]_100.csv (rede 100 Mbps)")

if __name__ == "__main__":
    main()