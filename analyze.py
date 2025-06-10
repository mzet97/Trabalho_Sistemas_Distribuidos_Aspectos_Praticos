#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import glob
import os
import statistics
from math import sqrt

Z_98 = 2.3263
EXPECTED_MEASURES = 1000
EXPECTED_MEASURES_PER_LEVEL = 100

def _filter_by_speed(paths, network_speed):
    """
    Retorna apenas os caminhos cujo nome corresponde à velocidade pedida.
    - Para 10 Mbps => NÃO deve conter '_100'
    - Para 100 Mbps => DEVE conter '_100'
    """
    if network_speed == "100":
        return [p for p in paths if "_100" in os.path.basename(p)]
    else:
        return [p for p in paths if "_100" not in os.path.basename(p)]

def read_raw_data(filepath):
    """
    Lê raw_data_clienteX[ _100].csv => { tamanho_bytes: [rtt1, rtt2, ...] }
    Descartamos rtt < 0 (timeouts).
    """
    data = {}
    total_per_size = {}

    if not os.path.exists(filepath):
        print(f"[WARN] Arquivo não encontrado: {filepath}")
        return data, total_per_size

    try:
        line_count = valid_count = invalid_count = 0
        with open(filepath, newline="") as f:
            reader = csv.DictReader(f)

            for row in reader:
                line_count += 1
                if "tamanho_bytes" not in row or "rtt_ms" not in row:
                    invalid_count += 1
                    continue

                try:
                    size = int(row["tamanho_bytes"])
                    rtt  = float(row["rtt_ms"])
                except (ValueError, TypeError):
                    invalid_count += 1
                    continue

                total_per_size[size] = total_per_size.get(size, 0) + 1
                if rtt < 0:              # timeout
                    continue

                data.setdefault(size, []).append(rtt)
                valid_count += 1

        print(f"[INFO] {filepath}: {line_count} linhas lidas, "
              f"{valid_count} RTTs válidos, {invalid_count} linhas inválidas")

    except Exception as e:
        print(f"[ERROR] Erro ao processar {filepath}: {e}")

    return data, total_per_size


def read_ramp_data(filepath):
    """
    Lê ramp_data_clienteX[ _100].csv
      => { (tamanho_bytes, nivel): [rtt1, rtt2, ...] }
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
                if ("tamanho_bytes" not in row or
                    "nivel" not in row or
                    "rtt_ms" not in row):
                    continue
                try:
                    size  = int(row["tamanho_bytes"])
                    nivel = int(row["nivel"])
                    rtt   = float(row["rtt_ms"])
                except (ValueError, TypeError):
                    continue
                if rtt < 0:
                    continue

                key = (size, nivel)
                total_per_key[key] = total_per_key.get(key, 0) + 1
                data.setdefault(key, []).append(rtt)

    except Exception as e:
        print(f"[ERROR] Erro ao processar {filepath}: {e}")

    return data, total_per_key

def detect_outliers(rtts):
    if len(rtts) < 4:
        return 0, []
    sorted_rtts = sorted(rtts)
    q1 = sorted_rtts[len(sorted_rtts) // 4]
    q3 = sorted_rtts[3 * len(sorted_rtts) // 4]
    iqr = q3 - q1
    low, up = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    outliers = [x for x in rtts if x < low or x > up]
    return len(outliers), outliers


def compute_percentile(sorted_data, p):
    if not sorted_data:
        return float("nan")
    k = (len(sorted_data) - 1) * p / 100
    f = int(k)
    c = k - f
    if f + 1 < len(sorted_data):
        return sorted_data[f] + c * (sorted_data[f + 1] - sorted_data[f])
    return sorted_data[f]


def compute_stats(rtts, total_attempts=None):
    n = len(rtts)
    if n == 0:
        return (0, *(float("nan"),) * 10, 100.0, 0)

    rtts_sorted = sorted(rtts)
    media   = statistics.mean(rtts_sorted)
    mediana = statistics.median(rtts_sorted)
    dp      = statistics.stdev(rtts_sorted) if n > 1 else 0.0
    jitter  = (statistics.mean([abs(rtts_sorted[i] - rtts_sorted[i - 1])
               for i in range(1, n)]) if n > 1 else 0.0)
    ic_half = Z_98 * (dp / sqrt(n)) if n > 1 else 0.0
    ic_low  = media - ic_half
    ic_up   = media + ic_half
    p95     = compute_percentile(rtts_sorted, 95)
    p99     = compute_percentile(rtts_sorted, 99)
    min_rtt, max_rtt = rtts_sorted[0], rtts_sorted[-1]
    taxa_perda = ((total_attempts - n) / total_attempts * 100
                  if total_attempts else 0.0)
    num_outliers, _ = detect_outliers(rtts_sorted)

    return (n, media, mediana, dp, jitter, ic_low, ic_up,
            p95, p99, min_rtt, max_rtt, taxa_perda, num_outliers)

def process_raw_files_by_network(network_speed):
    pattern = "raw_data_cliente*.csv"
    raw_files = _filter_by_speed(glob.glob(pattern), network_speed)

    if not raw_files:
        print(f"[INFO] Nenhum arquivo RAW para rede {network_speed} Mbps.")
        return False

    print(f"\n[INFO] Processando {len(raw_files)} arquivo(s) RAW "
          f"para rede {network_speed} Mbps...")

    for raw_path in sorted(raw_files):
        base     = os.path.basename(raw_path).replace("raw_data_", "").replace(".csv", "")
        out_path = f"stats_{base}.csv"

        data, total_per_size = read_raw_data(raw_path)
        if not data:
            print(f"[WARN] Sem dados válidos em {raw_path}")
            continue

        with open(out_path, "w", newline="") as fout:
            writer = csv.writer(fout)
            writer.writerow([
                "tamanho_bytes", "n_validos", "media_ms", "mediana_ms",
                "dp_ms", "jitter_ms", "ic_lower_ms", "ic_upper_ms",
                "p95_ms", "p99_ms", "min_ms", "max_ms",
                "taxa_perda_%", "num_outliers"
            ])

            for size in sorted(data.keys()):
                rtts = data[size]
                total = total_per_size.get(size, EXPECTED_MEASURES)
                stats = compute_stats(rtts, total)
                writer.writerow([
                    size, stats[0],
                    *(f"{x:.5f}" for x in stats[1:10]),
                    f"{stats[10]:.5f}", f"{stats[11]:.2f}", stats[12]
                ])

        print(f"[SUCCESS] Estatísticas salvas em {out_path}")
    return True

def process_ramp_files_by_network(network_speed):
    pattern = "ramp_data_cliente*.csv"
    ramp_files = _filter_by_speed(glob.glob(pattern), network_speed)

    if not ramp_files:
        print(f"[INFO] Nenhum arquivo RAMPA para rede {network_speed} Mbps.")
        return False

    print(f"\n[INFO] Processando {len(ramp_files)} arquivo(s) RAMPA "
          f"para rede {network_speed} Mbps...")

    for ramp_path in sorted(ramp_files):
        base     = os.path.basename(ramp_path).replace("ramp_data_", "").replace(".csv", "")
        out_path = f"stats_ramp_{base}.csv"

        data, total_per_key = read_ramp_data(ramp_path)
        if not data:
            print(f"[WARN] Sem dados válidos em {ramp_path}")
            continue

        with open(out_path, "w", newline="") as fout:
            writer = csv.writer(fout)
            writer.writerow([
                "tamanho_bytes", "nivel", "n_validos", "media_ms", "mediana_ms",
                "dp_ms", "jitter_ms", "ic_lower_ms", "ic_upper_ms",
                "p95_ms", "p99_ms", "min_ms", "max_ms",
                "taxa_perda_%", "num_outliers"
            ])

            for (size, nivel) in sorted(data.keys(), key=lambda x: (x[0], x[1])):
                rtts  = data[(size, nivel)]
                total = total_per_key.get((size, nivel), EXPECTED_MEASURES_PER_LEVEL)
                stats = compute_stats(rtts, total)
                writer.writerow([
                    size, nivel, stats[0],
                    *(f"{x:.5f}" for x in stats[1:10]),
                    f"{stats[10]:.5f}", f"{stats[11]:.2f}", stats[12]
                ])

        print(f"[SUCCESS] Estatísticas de rampa salvas em {out_path}")
    return True

def aggregate_clients_by_network(network_speed):
    pattern = "stats_cliente*.csv"
    stats_files = _filter_by_speed(glob.glob(pattern), network_speed)

    if len(stats_files) != 2:
        print(f"[WARN] Esperado 2 arquivos de estatísticas para rede {network_speed} Mbps, "
              f"encontrados {len(stats_files)}. Pulando agregação.")
        return False

    out_path = f"stats_network_{network_speed}mbps.csv"
    aggregated = {}

    for stats_file in stats_files:
        with open(stats_file, newline="") as f:
            for row in csv.DictReader(f):
                size = int(row["tamanho_bytes"])
                agg  = aggregated.setdefault(size, {
                    "media": [], "mediana": [], "p95": [], "p99": [],
                    "jitter": [], "taxa_perda": [], "n_total": 0
                })
                agg["media"].append(float(row["media_ms"]))
                agg["mediana"].append(float(row["mediana_ms"]))
                agg["p95"].append(float(row["p95_ms"]))
                agg["p99"].append(float(row["p99_ms"]))
                agg["jitter"].append(float(row["jitter_ms"]))
                agg["taxa_perda"].append(float(row["taxa_perda_%"]))
                agg["n_total"] += int(row["n_validos"])

    with open(out_path, "w", newline="") as fout:
        writer = csv.writer(fout)
        writer.writerow([
            "tamanho_bytes", "media_agregada_ms", "mediana_agregada_ms",
            "p95_agregado_ms", "p99_agregado_ms", "jitter_agregado_ms",
            "taxa_perda_agregada_%", "n_total_amostras"
        ])

        for size in sorted(aggregated):
            agg = aggregated[size]
            writer.writerow([
                size,
                *(f"{statistics.mean(agg[key]):.5f}" for key in
                  ("media", "mediana", "p95", "p99", "jitter")),
                f"{statistics.mean(agg['taxa_perda']):.2f}",
                agg["n_total"]
            ])

    print(f"[SUCCESS] Dados agregados salvos em {out_path}")
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
    print("[ANALYZE] Iniciando processamento…\n")

    if process_raw_files_by_network("10"):
        aggregate_clients_by_network("10")
    process_ramp_files_by_network("10")

    if process_raw_files_by_network("100"):
        aggregate_clients_by_network("100")
    process_ramp_files_by_network("100")

    generate_summary_report()


if __name__ == "__main__":
    main()
