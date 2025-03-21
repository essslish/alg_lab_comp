from compressor.base import Compressor


class MTFCompressor(Compressor):

    def __init__(self, alphabet_length: int = 256):
        """
        :param alphabet_length: длина алфавита (количество уникальных символов).
        """
        self.alphabet_length = alphabet_length

    def compress(self, data: bytes) -> bytes:
        """
        Преобразует входные данные с помощью алгоритма Move-To-Front (MTF).
        Для каждого байта определяется его индекс в алфавите,
        затем символ перемещается в начало списка.
        Возвращает последовательность индексов в виде байтов.
        """
        if not data:
            return b""

        # Инициализируем алфавит
        alphabet = list(range(self.alphabet_length))
        output = bytearray()

        for byte in data:
            index = alphabet.index(byte)
            output.append(index)
            # Перемещаем найденный байт в начало списка
            alphabet.pop(index)
            alphabet.insert(0, byte)

        return bytes(output)

    def decompress(self, data: bytes) -> bytes:
        """
        Обратное преобразование для алгоритма MTF.
        Для каждого индекса из входных данных:
        - Из текущего алфавита извлекается символ по указанному индексу.
        - Символ выводится, затем перемещается в начало алфавита.
        Возвращает восстановленную последовательность байтов.
        """
        if not data:
            return b""

        # Инициализируем алфавит
        alphabet = list(range(self.alphabet_length))
        output = bytearray()

        for index in data:
            byte = alphabet[index]
            output.append(byte)
            # Перемещаем символ в начало списка
            alphabet.pop(index)
            alphabet.insert(0, byte)

        return bytes(output)
