# experiments/entropy_analysis.py

import os

import matplotlib.pyplot as plt
import pandas as pd

from compressor.bwt import BWTCompressor
from compressor.mtf import MTFCompressor
from utils.metrics import entropy

ENWIK7 = "data/input/enwik7.txt"
PLOTS_DIR = "data/plots"

BLOCK_SIZES = [2 ** i for i in range(10, 21)]  # от 1KB до 1MB


def compute_block_entropy(path: str, block_size: int) -> float:
    total_symbols = 0
    total_entropy = 0.0

    mtf = MTFCompressor()
    with open(path, "rb") as f:
        while True:
            block = f.read(block_size)
            if not block:
                break
            last_column, _ = BWTCompressor.bwt_transform(block)
            transformed = mtf.compress(last_column)
            e = entropy(transformed)
            total_entropy += e * len(block)
            total_symbols += len(block)

    return total_entropy / total_symbols


def experiment_entropy():
    os.makedirs(PLOTS_DIR, exist_ok=True)
    results = []

    for size in BLOCK_SIZES:
        e = compute_block_entropy(ENWIK7, size)
        print(f"Block {size / 1024:.0f} KB → entropy={e:.4f}")
        results.append((size, e))

    df = pd.DataFrame(results, columns=["block_size", "entropy"])
    df.to_csv("data/entropy_vs_block.csv", index=False)

    plt.figure(figsize=(10, 5))
    plt.plot(df["block_size"] / 1024, df["entropy"], marker="o")
    plt.xscale("log", base=2)
    plt.title("Энтропия после BWT+MTF от размера блока (enwik7)")
    plt.xlabel("Размер блока, KB (лог₂ масштаб)")
    plt.ylabel("Энтропия (бит/символ)")
    plt.grid(True, which="both", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "entropy_vs_block.png"))
    plt.close()

    print(f"График сохранён → {PLOTS_DIR}/entropy_vs_block.png")
