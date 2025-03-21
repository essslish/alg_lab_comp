# visualize.py

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import TwoSlopeNorm

RESULTS_CSV = "data/results.csv"
PLOTS_DIR = "data/plots"


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def plot_per_file(df):
    for fname, group in df.groupby("filename"):
        algos = group["compressor"]
        ratio = group["compression_ratio"]
        comp_time = group["compression_time"]
        decomp_time = group["decompression_time"]

        fig, (ax1, ax2) = plt.subplots(nrows=2, figsize=(10, 14), gridspec_kw={"height_ratios": [1, 1.2]})

        # Коэффициент сжатия
        ax1.bar(algos, ratio)
        ax1.set_title(f"Коэффициент сжатия — {fname}")
        ax1.set_ylabel("Коэффициент сжатия")
        ax1.set_xticklabels(algos, rotation=45, ha="right")

        # Время
        x = np.arange(len(algos))
        width = 0.4
        ax2.bar(x - width / 2, comp_time, width, label="Время сжатия (с)")
        ax2.bar(x + width / 2, decomp_time, width, label="Время декомпрессии (с)")
        ax2.set_title(f"Время работы — {fname}")
        ax2.set_xticks(x)
        ax2.set_xticklabels(algos, rotation=45, ha="right")
        ax2.set_ylabel("Время (сек)")
        ax2.legend()

        plt.tight_layout()
        plt.savefig(os.path.join(PLOTS_DIR, f"{fname}_metrics.png"))
        plt.close()


def plot_overall_matrix(df):
    pivot = df.pivot_table(
        index="compressor",
        columns="filename",
        values="compression_ratio",
        aggfunc="mean"
    )

    fig, ax = plt.subplots(figsize=(max(10, pivot.shape[1] * 0.7), max(6, pivot.shape[0] * 0.5)))
    norm = TwoSlopeNorm(vmin=pivot.min().min(), vcenter=1.0, vmax=pivot.max().max())
    im = ax.imshow(pivot, cmap="RdBu_r", norm=norm, aspect="auto")

    # Подписи осей
    ax.set_xticks(np.arange(pivot.shape[1]))
    ax.set_xticklabels(pivot.columns, rotation=45, ha="right")
    ax.set_yticks(np.arange(pivot.shape[0]))
    ax.set_yticklabels(pivot.index)
    ax.set_title("Матрица коэффициента сжатия (алгоритм × файл)")
    ax.set_xlabel("Файл")
    ax.set_ylabel("Алгоритм")

    # Аннотируем значения внутри ячеек
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            val = pivot.iat[i, j]
            ax.text(j, i, f"{val:.3f}", ha="center", va="center", color="black")

    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Коэффициент сжатия")

    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "overall_matrix.png"))
    plt.close()


def main():
    ensure_dir(PLOTS_DIR)
    df = pd.read_csv(RESULTS_CSV)
    plot_per_file(df)
    plot_overall_matrix(df)
    print(f"Графики сохранены в {PLOTS_DIR}")


if __name__ == "__main__":
    main()
