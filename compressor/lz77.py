import struct

from compressor.base import Compressor


class LZ77Compressor(Compressor):
    def __init__(self, window_size: int = 10000, lookahead_buffer_size: int = 500):
        """
        :param window_size: размер буфера поиска (в байтах)
        :param lookahead_buffer_size: размер буфера просмотра (в байтах)
        """
        self.window_size = window_size
        self.lookahead_buffer_size = lookahead_buffer_size

    def compress(self, data: bytes) -> bytes:
        """
          - Для каждой позиции определяется буфер поиска (предыдущие данные)
            и Lookahead Buffer (следующие байты).
          - Находится наибольшее совпадение, и запоминается offset и length.
          - Если после совпадения ещё есть данные, формируется токен:
              (offset, length, next_symbol) – 5 байт.
          - Если входной поток заканчивается (pos + length == len(data)),
            формируется финальный токен: (offset, length) – 4 байта.
        """
        if not data:
            return b""

        pos = 0
        n = len(data)
        output = bytearray()

        while pos < n:
            start_index = max(0, pos - self.window_size)
            search_buffer = data[start_index:pos]

            match_length = 0
            match_offset = 0
            lookahead_limit = min(self.lookahead_buffer_size, n - pos)

            # Ищем наибольшее совпадение
            for length in range(1, lookahead_limit + 1):
                substring = data[pos: pos + length]
                index = search_buffer.rfind(substring)
                if index != -1:
                    match_length = length
                    match_offset = len(search_buffer) - index
                else:
                    break

            # Если после совпадения есть данные (полный токен)
            if pos + match_length < n:
                next_symbol = data[pos + match_length: pos + match_length + 1]
                output += struct.pack(">H", match_offset)
                output += struct.pack(">H", match_length)
                output += next_symbol
                pos += match_length + 1
            else:
                # Финальный токен: данных больше нет, поэтому только offset и length (4 байта)
                output += struct.pack(">H", match_offset)
                output += struct.pack(">H", match_length)
                pos = n

        return bytes(output)

    def decompress(self, data: bytes) -> bytes:
        """
          - Пока доступно 5 байт, читается токен (offset, length, next_symbol).
          - Если остаётся ровно 4 байта, обрабатывается финальный токен.
          - Для каждого токена, если offset и length не равны 0, из уже восстановленных данных
            копируется substring длины length, затем добавляется next_symbol (если он есть).
        """
        if not data:
            return b""

        pos = 0
        output = bytearray()
        n = len(data)

        while pos < n:
            # Если осталось 5 или более байт, обрабатываем полный токен
            if n - pos >= 5:
                offset = struct.unpack(">H", data[pos:pos + 2])[0]
                length = struct.unpack(">H", data[pos + 2:pos + 4])[0]
                next_symbol = data[pos + 4:pos + 5]
                pos += 5

                if offset == 0 and length == 0:
                    output += next_symbol
                else:
                    start_index = len(output) - offset
                    for i in range(length):
                        output.append(output[start_index + i])
                    output += next_symbol
            elif n - pos == 4:
                # Обработка финального токена (без next_symbol)
                offset = struct.unpack(">H", data[pos:pos + 2])[0]
                length = struct.unpack(">H", data[pos + 2:pos + 4])[0]
                pos += 4
                if offset != 0 or length != 0:
                    start_index = len(output) - offset
                    for i in range(length):
                        output.append(output[start_index + i])
            else:
                raise ValueError("Некорректный формат данных LZ77.")

        return bytes(output)
