from typing import List

from compressor.base import Compressor


class CombinedCompressor(Compressor):
    def __init__(self, compressors: List[Compressor]):
        """
        :param compressors: список объектов, реализующих интерфейс Compressor.
        """
        self.compressors = compressors

    def compress(self, data: bytes) -> bytes:
        """
        Последовательно применяет метод compress() для каждого алгоритма.
        """
        result = data
        for compressor in self.compressors:
            result = compressor.compress(result)
        return result

    def decompress(self, data: bytes) -> bytes:
        """
        Последовательно применяет метод decompress() для каждого алгоритма в обратном порядке.
        """
        result = data
        for compressor in reversed(self.compressors):
            result = compressor.decompress(result)
        return result
