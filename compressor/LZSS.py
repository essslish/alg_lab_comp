import struct

from compressor.base import Compressor


class LZSSCompressor(Compressor):
    def __init__(self, window_size=10000, lookahead_buffer_size=500, min_match_length=3):
        self.window_size = window_size
        self.lookahead_buffer_size = lookahead_buffer_size
        self.min_match_length = min_match_length

    def compress(self, data: bytes) -> bytes:
        """

        Для каждой позиции:
          - Ищется наибольшее совпадение в буфере поиска.
          - Если длина совпадения >= min_match_length, формируется ссылка:
              Токен ссылки: [flag=1 (1 байт)] + [offset (2 байта)] + [length (1 байт)].
              Позиция увеличивается на match_length.
          - Иначе, формируется литерал:
              Токен литерала: [flag=0 (1 байт)] + [literal (1 байт)].
              Позиция увеличивается на 1.
        """
        if not data:
            return b""
        pos, n = 0, len(data)
        out = bytearray()

        while pos < n:
            start = max(0, pos - self.window_size)
            search = data[start:pos]
            match_length = 0
            match_offset = 0
            limit = min(self.lookahead_buffer_size, n - pos)

            for length in range(1, limit + 1):
                idx = search.rfind(data[pos:pos + length])
                if idx != -1:
                    match_length = length
                    match_offset = len(search) - idx
                else:
                    break

            if match_length >= self.min_match_length:
                # ссылка: flag=1, offset (4 bytes), length (4 bytes)
                out += struct.pack(">BII", 1, match_offset, match_length)
                pos += match_length
            else:
                # литерал: flag=0 + байт
                out += struct.pack(">B", 0) + data[pos:pos + 1]
                pos += 1

        return bytes(out)

    def decompress(self, data: bytes) -> bytes:
        """
        - Если флаг равен 0, читается литерал (1 байт) и добавляется в выход.
        - Если флаг равен 1, читаются offset (2 байта) и length (1 байт). Из уже восстановленных данных копируется
        последовательность длиной length, начиная с позиции: len(output) - offset.
        """
        if not data:
            return b""
        pos, n = 0, len(data)
        out = bytearray()

        while pos < n:
            flag = data[pos]
            pos += 1

            if flag == 0:
                out += data[pos:pos + 1]
                pos += 1
            elif flag == 1:
                offset, length = struct.unpack(">II", data[pos:pos + 8])
                pos += 8
                start = len(out) - offset
                out.extend(out[start:start + length])
            else:
                raise ValueError(f"Unknown LZSS flag: {flag}")

        return bytes(out)
