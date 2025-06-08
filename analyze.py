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
    Lê raw_data_clienteX.csv e retorna dicionário:
      { tamanho_bytes: [rtt1, rtt2, ...] }
    Descartamos rtt < 0 (timeouts).
    """
    data = {}
    total_per_size = {}
    
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            size = int(row["tamanho_bytes"])
            total_per_size[size] = total_per_size.get(size, 0) + 1
            
            try:
                rtt = float(row["rtt_ms"])
            except ValueError:
                continue
            if rtt < 0:
                continue
            data.setdefault(size, []).append(rtt)
    
    return data, total_per_size

def read_ramp_data(filepath):
    """
    Lê ramp_data_clienteX.csv e retorna dicionário:
      { (tamanho_bytes, nivel): [rtt1, rtt2, ...] }
    Descartamos rtt < 0 (timeouts).
    """
    data = {}
    total_per_key = {}
    
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            size = int(row["tamanho_bytes"])
            nivel = int(row["nivel"])
            key = (size, nivel)
            total_per_key[key] = total_per_key.get(key, 0) + 1
            
            try:
                rtt = float(row["rtt_ms"])
            except ValueError:
                continue
            if rtt < 0:
                continue
            data.setdefault(key, []).append(rtt)
    
    return data, total_per_key

def detect_outliers(rtts):
    """
    Detecta outliers usando método IQR (Interquartile Range).
    Retorna número de outliers e lista dos valores outliers.
    """
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
    Recebe lista de RTTs (float) e retorna uma tupla expandida com:
    (n, media, mediana, dp, jitter, ic_lower, ic_upper, p95, p99, 
     min_rtt, max_rtt, taxa_perda, num_outliers)
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

def aggregate_ramp_by_size(ramp_data, total_data):
    """
    Agrega dados de rampa por tamanho, ignorando níveis.
    Útil para ver o comportamento geral por tamanho.
    """
    by_size = {}
    total_by_size = {}
    
    for (size, nivel), rtts in ramp_data.items():
        by_size.setdefault(size, []).extend(rtts)
        total_by_size[size] = total_by_size.get(size, 0) + total_data.get((size, nivel), 0)
    
    return by_size, total_by_size

def find_saturation_level(ramp_data, size_bytes):
    """
    Identifica o nível onde ocorre saturação (aumento significativo no RTT).
    Retorna o nível de saturação ou None se não detectado.
    """
    levels = []
    mean_rtts = []
    
    for nivel in range(1, 20):
        key = (size_bytes, nivel)
        if key in ramp_data and len(ramp_data[key]) > 0:
            mean_rtt = statistics.mean(ramp_data[key])
            levels.append(nivel)
            mean_rtts.append(mean_rtt)
    
    if len(levels) < 3:
        return None
    
    baseline = mean_rtts[0]
    for i, (nivel, mean_rtt) in enumerate(zip(levels, mean_rtts)):
        if mean_rtt > baseline * 1.5:
            return nivel
    
    return None

def process_raw_files():
    """
    Para cada raw_data_clienteX.csv, gera stats_clienteX.csv
    por tamanho de payload com estatísticas expandidas.
    """
    for raw_path in glob.glob("raw_data_cliente*.csv"):
        base = os.path.basename(raw_path).replace("raw_data_", "").replace(".csv", "")
        out_path = f"stats_{base}.csv"

        data, total_per_size = read_raw_data(raw_path)
        sizes = sorted(data.keys())

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
                    stats[0],  # n_validos
                    f"{stats[1]:.5f}",  # media
                    f"{stats[2]:.5f}",  # mediana
                    f"{stats[3]:.5f}",  # dp
                    f"{stats[4]:.5f}",  # jitter
                    f"{stats[5]:.5f}",  # ic_lower
                    f"{stats[6]:.5f}",  # ic_upper
                    f"{stats[7]:.5f}",  # p95
                    f"{stats[8]:.5f}",  # p99
                    f"{stats[9]:.5f}",  # min
                    f"{stats[10]:.5f}",  # max
                    f"{stats[11]:.2f}",  # taxa_perda
                    stats[12]  # num_outliers
                ])

        print(f"[ANALYZE] Estatísticas (raw) gravadas em {out_path}")

def process_ramp_files():
    """
    Para cada ramp_data_clienteX.csv, gera:
    1. stats_ramp_clienteX.csv - por (tamanho_bytes, nivel)
    2. stats_ramp_aggregated_clienteX.csv - agregado por tamanho
    """
    for ramp_path in glob.glob("ramp_data_cliente*.csv"):
        base = os.path.basename(ramp_path).replace("ramp_data_", "").replace(".csv", "")
        out_path = f"stats_ramp_{base}.csv"
        out_path_agg = f"stats_ramp_aggregated_{base}.csv"

        data, total_per_key = read_ramp_data(ramp_path)
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
                    stats[0],  # n_validos
                    f"{stats[1]:.5f}",  # media
                    f"{stats[2]:.5f}",  # mediana
                    f"{stats[3]:.5f}",  # dp
                    f"{stats[4]:.5f}",  # jitter
                    f"{stats[5]:.5f}",  # ic_lower
                    f"{stats[6]:.5f}",  # ic_upper
                    f"{stats[7]:.5f}",  # p95
                    f"{stats[8]:.5f}",  # p99
                    f"{stats[9]:.5f}",  # min
                    f"{stats[10]:.5f}",  # max
                    f"{stats[11]:.2f}",  # taxa_perda
                    stats[12]  # num_outliers
                ])

        print(f"[ANALYZE] Estatísticas (rampa) gravadas em {out_path}")
        
        agg_data, agg_total = aggregate_ramp_by_size(data, total_per_key)
        sizes = sorted(agg_data.keys())
        
        with open(out_path_agg, "w", newline="") as fout:
            writer = csv.writer(fout)
            writer.writerow([
                "tamanho_bytes", "n_total", "media_ms",
                "mediana_ms", "dp_ms", "jitter_ms",
                "p95_ms", "p99_ms", "min_ms", "max_ms",
                "taxa_perda_%", "nivel_saturacao"
            ])
            
            for size in sizes:
                rtts = agg_data[size]
                total_attempts = agg_total.get(size, EXPECTED_MEASURES_PER_LEVEL * 19)
                stats = compute_stats(rtts, total_attempts)
                saturation_level = find_saturation_level(data, size)
                
                writer.writerow([
                    size,
                    stats[0],  # n_total
                    f"{stats[1]:.5f}",  # media
                    f"{stats[2]:.5f}",  # mediana
                    f"{stats[3]:.5f}",  # dp
                    f"{stats[4]:.5f}",  # jitter
                    f"{stats[7]:.5f}",  # p95
                    f"{stats[8]:.5f}",  # p99
                    f"{stats[9]:.5f}",  # min
                    f"{stats[10]:.5f}",  # max
                    f"{stats[11]:.2f}",  # taxa_perda
                    saturation_level if saturation_level else "N/A"
                ])
        
        print(f"[ANALYZE] Estatísticas agregadas (rampa) gravadas em {out_path_agg}")

def generate_summary_report():
    """
    Gera um relatório resumido da análise para todos os experimentos.
    """
    print("\n" + "="*60)
    print("RESUMO DA ANÁLISE DE DESEMPENHO UDP")
    print("="*60)
    
    for client_id in [1, 2]:
        stats_file = f"stats_cliente{client_id}.csv"
        if not os.path.exists(stats_file):
            continue
            
        print(f"\n### EXPERIMENTO 1 - Cliente {client_id} ###")
        
        with open(stats_file, newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            if not rows:
                print("Sem dados disponíveis")
                continue
            
            all_min = min(float(r["min_ms"]) for r in rows)
            all_max = max(float(r["max_ms"]) for r in rows)
            
            avg_loss = statistics.mean(float(r["taxa_perda_%"]) for r in rows)
            
            max_std_row = max(rows, key=lambda r: float(r["dp_ms"]))
            
            total_outliers = sum(int(r["num_outliers"]) for r in rows)
            
            print(f"RTT mínimo global: {all_min:.3f} ms")
            print(f"RTT máximo global: {all_max:.3f} ms")
            print(f"Taxa de perda média: {avg_loss:.2f}%")
            print(f"Tamanho com maior variabilidade: {max_std_row['tamanho_bytes']} bytes")
            print(f"  - Desvio padrão: {float(max_std_row['dp_ms']):.3f} ms")
            print(f"Total de outliers detectados: {total_outliers}")
    
    for client_id in [1, 2]:
        stats_file = f"stats_ramp_aggregated_cliente{client_id}.csv"
        if not os.path.exists(stats_file):
            continue
            
        print(f"\n### EXPERIMENTO 2 (RAMPA) - Cliente {client_id} ###")
        
        with open(stats_file, newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            if not rows:
                print("Sem dados disponíveis")
                continue
            
            saturation_info = []
            for r in rows:
                if r["nivel_saturacao"] != "N/A":
                    saturation_info.append({
                        "size": int(r["tamanho_bytes"]),
                        "level": int(r["nivel_saturacao"])
                    })
            
            if saturation_info:
                print("Níveis de saturação detectados:")
                for info in sorted(saturation_info, key=lambda x: x["size"]):
                    taxa = 10 + ((100 - 10) * (info["level"] - 1) / 9)
                    print(f"  - {info['size']} bytes: nível {info['level']} (~{taxa:.0f} req/s)")
            else:
                print("Nenhuma saturação detectada nos níveis testados")
            
            avg_p95 = statistics.mean(float(r["p95_ms"]) for r in rows)
            avg_p99 = statistics.mean(float(r["p99_ms"]) for r in rows)
            
            print(f"P95 médio (todos os tamanhos): {avg_p95:.3f} ms")
            print(f"P99 médio (todos os tamanhos): {avg_p99:.3f} ms")
    
    print("\n" + "="*60)
    print("Análise concluída. Verifique os arquivos CSV e PNG gerados.")
    print("="*60 + "\n")

def main():
    print("[ANALYZE] Iniciando processamento dos dados...")
    
    process_raw_files()
    
    process_ramp_files()
    
    generate_summary_report()

if __name__ == "__main__":
    main()