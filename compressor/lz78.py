import struct

from compressor.base import Compressor


class LZ78Compressor(Compressor):
    def __init__(self, max_dictionary_size: int = None):
        """
        :param max_dictionary_size: опциональное ограничение размера словаря (не используется в данной реализации)
        """
        self.max_dictionary_size = max_dictionary_size

    def compress(self, data: bytes) -> bytes:
        """
        Выходной формат:
          - Для "полной" пары: 2 байта для индекса и 1 байт для символа.
          - Для последней неполной пары (если есть): 2 байта.
        """
        if not data:
            return b""
        dictionary = {}
        next_index = 1
        output = bytearray()
        pos = 0
        n = len(data)

        while pos < n:
            current = b""
            while pos < n:
                candidate = current + data[pos:pos + 1]
                if candidate in dictionary:
                    current = candidate
                    pos += 1
                else:
                    break

            if pos < n:
                prefix_index = dictionary.get(current, 0)
                output += struct.pack(">I", prefix_index) + data[pos:pos + 1]
                dictionary[current + data[pos:pos + 1]] = next_index
                next_index += 1
                pos += 1
            else:
                if current:
                    prefix_index = dictionary.get(current, 0)
                    output += struct.pack(">I", prefix_index)
                break

        return bytes(output)

    def decompress(self, data: bytes) -> bytes:
        """
          - Пока остаётся не менее 3 байт, читаем пару (2 байта – индекс, 1 байт – символ),
            формируем новую последовательность: dictionary[index] + символ, добавляем её в словарь и выводим.
          - Если остаётся ровно 2 байта, читаем финальный индекс и выводим соответствующую последовательность из словаря.
        """
        if not data:
            return b""
        dictionary = {0: b""}
        next_index = 1
        output = bytearray()
        pos = 0
        n = len(data)

        while pos < n:
            if n - pos >= 5:
                prefix_index = struct.unpack(">I", data[pos:pos + 4])[0]
                symbol = data[pos + 4:pos + 5]
                pos += 5
                entry = dictionary.get(prefix_index, b"") + symbol
                output += entry
                dictionary[next_index] = entry
                next_index += 1
            elif n - pos == 4:
                prefix_index = struct.unpack(">I", data[pos:pos + 4])[0]
                pos += 4
                output += dictionary.get(prefix_index, b"")
            else:
                raise ValueError("Некорректный формат данных LZ78.")
        return bytes(output)
