import csv
import os
import time

from compressor.LZSS import LZSSCompressor
from compressor.LZW import LZWCompressor
from compressor.bwt import BWTCompressor
from compressor.combined import CombinedCompressor
from compressor.ha import HACompressor
from compressor.lz77 import LZ77Compressor
from compressor.lz78 import LZ78Compressor
from compressor.mtf import MTFCompressor
from compressor.rle import RLECompressor
from utils.logger import logger
from utils.metrics import calculate_metrics, save_raw_data_to_file

HEADERS = [
    "filename", "compressor",
    "original_size", "compressed_size", "decompressed_size", "compression_ratio",
    "compression_time", "decompression_time"
]


class ExperimentRunner:

    def __init__(self, test_files: dict, results_file: str = "data/results.csv"):
        self.test_files = test_files
        self.results_file = results_file
        self.compressors = {
            "HA": HACompressor(),
            "BWT": BWTCompressor(block_size=512),
            "MTF": MTFCompressor(),
            "RLE": RLECompressor(),
            "LZ77": LZ77Compressor(window_size=10000, lookahead_buffer_size=500),
            "LZ78": LZ78Compressor(),
            "LZSS": LZSSCompressor(window_size=10000, lookahead_buffer_size=500, min_match_length=3),
            "LZW": LZWCompressor(),
            "BWT+RLE": CombinedCompressor([BWTCompressor(block_size=512), RLECompressor()]),
            "BWT+MTF+HA": CombinedCompressor([BWTCompressor(block_size=512), MTFCompressor(), HACompressor()]),
            "BWT+MTF+RLE+HA": CombinedCompressor(
                [BWTCompressor(block_size=512),
                 MTFCompressor(),
                 RLECompressor(),
                 HACompressor()]),
            "LZSS+HA": CombinedCompressor(
                [LZSSCompressor(window_size=10000, lookahead_buffer_size=500, min_match_length=3),
                 HACompressor()]),
            "LZW+HA": CombinedCompressor([LZWCompressor(),
                                          HACompressor()]),
        }
        # Create results file with header
        if not os.path.exists(self.results_file):
            with open(self.results_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(HEADERS)

    def run_all(self):
        for filename, data in self.test_files.items():
            logger.info(f"===================== Тестируем файл: {filename} =====================\n")
            for name, compressor in self.compressors.items():
                logger.info(f"Компрессор: {name}")
                try:
                    start = time.perf_counter()
                    compressed = compressor.compress(data)
                    comp_time = time.perf_counter() - start

                    save_raw_data_to_file(compressed, f"data/compressed/{name}_{filename}")

                    start = time.perf_counter()
                    decompressed = compressor.decompress(compressed)
                    decomp_time = time.perf_counter() - start

                    save_raw_data_to_file(decompressed, f"data/decompressed/{name}_{filename}")

                except Exception as e:
                    logger.error(f"Ошибка при работе с алгоритмом {name}: {e}")
                    continue

                # Проверка корректности декомпрессии
                if decompressed == data:
                    logger.info("Корректная компрессия/декомпрессия.")
                else:
                    logger.error("Ошибка: данные не восстановились корректно.")

                # Вычисление прочих метрик (размеры, коэффициент сжатия)
                metrics = calculate_metrics(data, compressed, decompressed)
                row = [
                    filename, name,
                    metrics["original_size"],
                    metrics["compressed_size"],
                    metrics["decompressed_size"],
                    metrics["compression_ratio"],
                    round(comp_time, 6),
                    round(decomp_time, 6)
                ]

                with open(self.results_file, "a", newline="") as f:
                    csv.writer(f).writerow(row)

                logger.info(f"Метрики: {metrics['compression_ratio']:.2f}x сжатие, "
                            f"{metrics['original_size']}->{metrics['compressed_size']}, "
                            f"{comp_time:.4f} сек сжатие, "
                            f"{decomp_time:.4f} сек декомпрессия.")
