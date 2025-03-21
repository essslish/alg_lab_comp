# experiments/lzss_buffer_experiment.py

import os
import time

import matplotlib.pyplot as plt
import pandas as pd

from compressor.LZSS import LZSSCompressor
from utils.file_utils import load_test_file

DATA_FILE = "../data/input/enwik7.txt"
RESULTS_CSV = "../data/lzss_buffer_results.csv"
PLOT_FILE = "../data/plots/lzss_buffer.png"
# от 64 байт до 32 КБ
BUFFER_SIZES = [2 ** i for i in range(6, 16)]


def run_experiment():
    os.makedirs(os.path.dirname(RESULTS_CSV), exist_ok=True)
    os.makedirs(os.path.dirname(PLOT_FILE), exist_ok=True)

    data = load_test_file(DATA_FILE)
    original_size = len(data)

    rows = []
    for buf in BUFFER_SIZES:
        compressor = LZSSCompressor(window_size=buf, lookahead_buffer_size=buf//2, min_match_length=3)

        start = time.perf_counter()
        compressed = compressor.compress(data)
        comp_time = time.perf_counter() - start

        start = time.perf_counter()
        decompressed = compressor.decompress(compressed)
        decomp_time = time.perf_counter() - start

        assert decompressed == data, f"Ошибка восстановления при буфере {buf}"

        compressed_size = len(compressed)
        ratio = round(original_size / compressed_size, 3)

        rows.append({
            "buffer_size": buf,
            "original_size": original_size,
            "compressed_size": compressed_size,
            "compression_ratio": ratio,
            "compression_time": comp_time,
            "decompression_time": decomp_time
        })
        print(f"Буфер {buf:4d}B → ratio={ratio:.3f}, comp={comp_time:.3f}s, decomp={decomp_time:.3f}s")

    df = pd.DataFrame(rows)
    df.to_csv(RESULTS_CSV, index=False)
    plot_results(df)


def plot_results(df):
    fig, (ax1, ax2) = plt.subplots(nrows=2, figsize=(10, 8), sharex=True)

    ax1.plot(df["buffer_size"] / 1024, df["compression_ratio"], marker="o")
    ax1.set_xscale("log", base=2)
    ax1.set_title("Зависимость коэффициента сжатия от размера буфера (LZSS)")
    ax1.set_ylabel("Коэффициент сжатия")

    ax2.plot(df["buffer_size"] / 1024, df["compression_time"], marker="^", label="Время сжатия")
    ax2.plot(df["buffer_size"] / 1024, df["decompression_time"], marker="o", label="Время декомпрессии")
    ax2.set_xscale("log", base=2)
    ax2.set_title("Время работы алгоритма (LZSS)")
    ax2.set_xlabel("Размер буфера, KiB (лог₂ масштаб)")
    ax2.set_ylabel("Время (сек)")
    ax2.legend()

    plt.tight_layout()
    plt.savefig(PLOT_FILE)
    plt.close()
    print(f"График сохранён → {PLOT_FILE}")


if __name__ == "__main__":
    run_experiment()
