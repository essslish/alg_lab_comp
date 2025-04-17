import struct

from compressor.base import Compressor


class LZWCompressor(Compressor):
    def compress(self, data: bytes) -> bytes:
        """
        Изначально словарь содержит все возможные байты (0-255).
        Выводится последовательность кодов, каждый из которых упаковывается в 4 байта (32 бита, big-endian).
        """
        if not data:
            return b""

        # Инициализация словаря: ключ – байтовая последовательность, значение – её код.
        dictionary = {bytes([i]): i for i in range(256)}
        dict_size = 256

        w = b""
        result_codes = []

        for byte in data:
            c = bytes([byte])
            wc = w + c
            if wc in dictionary:
                w = wc
            else:
                result_codes.append(dictionary[w])
                # Добавляем новую последовательность wc в словарь
                dictionary[wc] = dict_size
                dict_size += 1
                w = c

        if w:
            result_codes.append(dictionary[w])

        # Упаковка кодов в байты (каждый код – 4 байта, big-endian)
        compressed_data = bytearray()
        for code in result_codes:
            compressed_data += struct.pack(">I", code)

        return bytes(compressed_data)

    def decompress(self, data: bytes) -> bytes:
        
        if not data:
            return b""

        # Извлечение кодов: каждый код занимает 4 байта
        codes = []
        for i in range(0, len(data), 4):
            code = struct.unpack(">I", data[i:i + 4])[0]
            codes.append(code)

        # Инициализация словаря: код -> байтовая последовательность
        dictionary = {i: bytes([i]) for i in range(256)}
        dict_size = 256

        # Первый код
        w = dictionary[codes[0]]
        result = bytearray(w)

        for k in codes[1:]:
            if k in dictionary:
                entry = dictionary[k]
            elif k == dict_size:
                entry = w + w[:1]
            else:
                raise ValueError("Некорректный код LZW: {}".format(k))

            result.extend(entry)

            # Добавляем новую последовательность в словарь
            dictionary[dict_size] = w + entry[:1]
            dict_size += 1

            w = entry

        return bytes(result)
