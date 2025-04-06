from compressor.base import Compressor


class OLD_RLECompressor(Compressor):
    def __init__(self, min_run_length: int = 1):
        """
        :param min_run_length: минимальное число повторов для кодирования (по умолчанию 1)
        """
        self.min_run_length = min_run_length

    def compress(self, data: bytes) -> bytes:
        """
        Сжимает данные с использованием алгоритма OLD_RLE.
        Алгоритм заменяет последовательности повторяющихся байтов парами: (count, value)
        """
        if not data:
            return b""

        compressed = bytearray()
        n = len(data)
        i = 0

        while i < n:
            current_byte = data[i]
            count = 1
            # Подсчёт количества повторов
            while (i + count < n) and (data[i + count] == current_byte) and (count < 255):
                count += 1

            # Если количество повторов меньше минимального порога, кодируем как отдельную пару.
            # Можно изменить стратегию обработки "литералов", но в данном случае мы всегда кодируем как (count, value)
            compressed.append(count)
            compressed.append(current_byte)

            i += count

        return bytes(compressed)

    def decompress(self, data: bytes) -> bytes:
        """
        Восстанавливает исходные данные, декодируя последовательность пар (count, value).
        """
        if not data:
            return b""

        decompressed = bytearray()
        n = len(data)

        # Ожидается, что данные состоят из пар
        if n % 2 != 0:
            raise ValueError("Некорректные данные для OLD_RLE-декомпрессии: нечётное число байтов.")

        for i in range(0, n, 2):
            count = data[i]
            value = data[i + 1]
            decompressed.extend([value] * count)

        return bytes(decompressed)
