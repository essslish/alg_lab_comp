"""
Комбинирующий класс, позволяющий последовательно применять любое количество алгоритмов.
При сжатии алгоритмы применяются в порядке, переданном в конструктор,
а при восстановлении — в обратном порядке.
Также замеряется время работы каждого шага и суммарное время.
"""

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
        Возвращает финальный сжатый поток.
        """
        result = data
        for compressor in self.compressors:
            result = compressor.compress(result)
        return result

    def decompress(self, data: bytes) -> bytes:
        """
        Последовательно применяет метод decompress() для каждого алгоритма в обратном порядке.
        Возвращает восстановленные данные.
        """
        result = data
        for compressor in reversed(self.compressors):
            result = compressor.decompress(result)
        return result
