import csv
import glob
import os
import statistics
from math import sqrt

Z_98 = 2.3263

def read_raw_data(filepath):
    """
    Lê raw_data_clienteX.csv e retorna dicionário:
      { tamanho_bytes: [rtt1, rtt2, ...] }
    Descartamos rtt < 0 (timeouts).
    """
    data = {}
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            size = int(row["tamanho_bytes"])
            try:
                rtt = float(row["rtt_ms"])
            except ValueError:
                continue
            if rtt < 0:
                continue
            data.setdefault(size, []).append(rtt)
    return data

def read_ramp_data(filepath):
    """
    Lê ramp_data_clienteX.csv e retorna dicionário:
      { (tamanho_bytes, nivel): [rtt1, rtt2, ...] }
    Descartamos rtt < 0 (timeouts).
    """
    data = {}
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            size = int(row["tamanho_bytes"])
            nivel = int(row["nivel"])
            try:
                rtt = float(row["rtt_ms"])
            except ValueError:
                continue
            if rtt < 0:
                continue
            key = (size, nivel)
            data.setdefault(key, []).append(rtt)
    return data

def compute_stats(rtts):
    """
    Recebe lista de RTTs (float) e retorna uma tupla:
    (n, media, mediana, dp, jitter, ic_lower, ic_upper)
    """
    n = len(rtts)
    if n == 0:
        return (0, float("nan"), float("nan"), float("nan"),
                float("nan"), float("nan"), float("nan"))

    rtts_sorted = sorted(rtts)
    media = statistics.mean(rtts_sorted)
    mediana = statistics.median(rtts_sorted)
    dp = statistics.stdev(rtts_sorted) if n > 1 else 0.0

    if n > 1:
        diffs = [abs(rtts_sorted[i] - rtts_sorted[i - 1]) for i in range(1, n)]
        jitter = statistics.mean(diffs)
    else:
        jitter = 0.0

    ic_half = Z_98 * (dp / sqrt(n)) if n > 1 else 0.0
    ic_low = media - ic_half
    ic_up  = media + ic_half
    return (n, media, mediana, dp, jitter, ic_low, ic_up)

def process_raw_files():
    """
    Para cada raw_data_clienteX.csv, gera stats_clienteX.csv
    por tamanho de payload.
    """
    for raw_path in glob.glob("raw_data_cliente*.csv"):
        base = os.path.basename(raw_path).replace("raw_data_", "").replace(".csv", "")
        out_path = f"stats_{base}.csv"

        data = read_raw_data(raw_path)
        sizes = sorted(data.keys())

        with open(out_path, "w", newline="") as fout:
            writer = csv.writer(fout)
            writer.writerow([
                "tamanho_bytes", "n_validos", "media_ms",
                "mediana_ms", "dp_ms", "jitter_ms",
                "ic_lower_ms", "ic_upper_ms"
            ])
            for size in sizes:
                rtts = data[size]
                n, media, mediana, dp, jitter, ic_low, ic_up = compute_stats(rtts)
                writer.writerow([
                    size,
                    n,
                    f"{media:.5f}",
                    f"{mediana:.5f}",
                    f"{dp:.5f}",
                    f"{jitter:.5f}",
                    f"{ic_low:.5f}",
                    f"{ic_up:.5f}"
                ])

        print(f"[ANALYZE] Estatísticas (raw) gravadas em {out_path}")

def process_ramp_files():
    """
    Para cada ramp_data_clienteX.csv, gera stats_ramp_clienteX.csv
    por (tamanho_bytes, nivel).
    """
    for ramp_path in glob.glob("ramp_data_cliente*.csv"):
        base = os.path.basename(ramp_path).replace("ramp_data_", "").replace(".csv", "")
        out_path = f"stats_ramp_{base}.csv"

        data = read_ramp_data(ramp_path)
        # Ordena por tamanho asc e depois nível asc
        keys = sorted(data.keys(), key=lambda x: (x[0], x[1]))

        with open(out_path, "w", newline="") as fout:
            writer = csv.writer(fout)
            writer.writerow([
                "tamanho_bytes", "nivel", "n_validos",
                "media_ms", "mediana_ms", "dp_ms",
                "jitter_ms", "ic_lower_ms", "ic_upper_ms"
            ])
            for (size, nivel) in keys:
                rtts = data[(size, nivel)]
                n, media, mediana, dp, jitter, ic_low, ic_up = compute_stats(rtts)
                writer.writerow([
                    size,
                    nivel,
                    n,
                    f"{media:.5f}",
                    f"{mediana:.5f}",
                    f"{dp:.5f}",
                    f"{jitter:.5f}",
                    f"{ic_low:.5f}",
                    f"{ic_up:.5f}"
                ])

        print(f"[ANALYZE] Estatísticas (rampa) gravadas em {out_path}")

def main():
    process_raw_files()
    process_ramp_files()

if __name__ == "__main__":
    main()
