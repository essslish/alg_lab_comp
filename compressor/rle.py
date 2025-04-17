from compressor.base import Compressor


class RLECompressor(Compressor):
    def __init__(self, min_run_length: int = 2):
        """
        :param min_run_length: минимальная длина последовательности одинаковых байтов,
        при которой она будет считаться повторяющейся.
        Всё, что короче — будет обрабатываться как уникальная последовательность (литерал).
        """
        self.min_run_length = min_run_length

    def compress(self, data: bytes) -> bytes:
       
        if not data:
            return b""

        compressed = bytearray()
        i = 0
        n = len(data)

        while i < n:
            run_start = i
            run_char = data[i]
            run_length = 1
            
            # Ограничиваем длину максимальным значением — 127 (7 бит)
            while i + 1 < n and data[i + 1] == run_char and run_length < 127:
                i += 1
                run_length += 1

            if run_length >= self.min_run_length:
                # Если повторов достаточно — записываем их как блок повторений
                # Старший бит не устанавливаем (0), остальные 7 бит — длина
                control_byte = run_length & 0b01111111  # Сброс старшего бита на всякий случай
                compressed.append(control_byte)  
                compressed.append(run_char)  
                i += 1  # Переходим к следующему байту после серии
            else:
                unique_start = run_start
                unique_seq = bytearray()

                
                while (i < n) and (
                        (i + 1 >= n or data[i + 1] != data[i])
                        or (i - unique_start + 1 < self.min_run_length)
                ) and (len(unique_seq) < 127):
                    unique_seq.append(data[i]) 
                    i += 1  

                # Формируем управляющий байт: старший бит = 1 (литерал), остальные 7 бит — длина
                control_byte = 0b10000000 | len(unique_seq)
                compressed.append(control_byte)  
                compressed.extend(unique_seq)  

        return bytes(compressed)

    def decompress(self, data: bytes) -> bytes:
       
        if not data:
            return b""

        decompressed = bytearray()
        i = 0
        n = len(data)

        while i < n:
            control_byte = data[i]
            i += 1

            # Определяем тип блока: если старший бит = 1, это литерал (уникальные байты)
            is_literal = (control_byte & 0b10000000) != 0
            # Получаем длину блока, отбросив старший бит
            length = control_byte & 0b01111111

            if is_literal:
                if i + length > n:
                    raise ValueError("Некорректные данные: длина литералов превышает оставшиеся байты.")
                decompressed.extend(data[i:i + length])  
                i += length
            else:
                if i >= n:
                    raise ValueError("Некорректные данные: отсутствует байт для повторения.")
                byte = data[i]
                decompressed.extend([byte] * length)  
                i += 1

        return bytes(decompressed)
