import queue

class Node:
    def __init__(self, symbol=None, counter=0):
        self.symbol = symbol
        self.counter = counter
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.counter < other.counter

def count_symb(S):
    counter = [0] * 128  # Массив для подсчета частоты символов
    for s in S:
        counter[ord(s)] += 1
    return counter

def build_huffman_tree(S):
    C = count_symb(S)
    Q = queue.PriorityQueue()

    # Формируем листы
    for i in range(128):
        if C[i] != 0:
            leaf = Node(symbol=chr(i), counter=C[i])
            Q.put(leaf)

    # Строим дерево
    while Q.qsize() > 1:
        left = Q.get()
        right = Q.get()
        merged = Node(counter=left.counter + right.counter)
        merged.left = left
        merged.right = right
        Q.put(merged)

    return Q.get()  # Возвращаем корень дерева

def generate_codes(node, code="", codes=None):
    if codes is None:
        codes = {}
    if node.symbol is not None:
        codes[node.symbol] = code
        return codes

    generate_codes(node.left, code + "0", codes)
    generate_codes(node.right, code + "1", codes)
    return codes

def huffman_encode(S):
    root = build_huffman_tree(S)
    codebook = generate_codes(root)
    coded_message = ""
    for s in S:
        coded_message += codebook.get(s, "")
    return codebook, coded_message

def huffman_decode(coded_message, codebook):
    reverse_codebook = {v: k for k, v in codebook.items()}
    current_code = ''
    decoded_str = ''
    
    for bit in coded_message:
        current_code += bit
        if current_code in reverse_codebook:
            decoded_str += reverse_codebook[current_code]
            current_code = ''

    return decoded_str

def bwt_transform(data):
    n = len(data)
    shifts = [data[i:] + data[:i] for i in range(n)]
    sorted_shifts = sorted(shifts)
    last_column = ''.join(shift[-1] for shift in sorted_shifts)
    return last_column

def bwt_inverse(last_column):
    n = len(last_column)
    table = [''] * n
    for _ in range(n):
        table = sorted(last_column[i] + table[i] for i in range(n))
    return table[0]

def move_to_front(data):
    result = []
    alphabet = []  # Пустой список для букв Alfabeta
    for symbol in data:
        if symbol in alphabet:
            alphabet.remove(symbol)  # Удаляем символ, если он уже есть
        alphabet.insert(0, symbol)  # Добавляем в начало
        result.append(symbol)
    return ''.join(result)

def inverse_move_to_front(data):
    result = []
    alphabet = []  # Пустой список для букв Alfabeta
    for symbol in data:
        result.append(symbol)  # Добавляем символ в результат
        if symbol in alphabet:
            alphabet.remove(symbol)  # Удаляем, если символ есть
        alphabet.insert(0, symbol)  # Вставляем его в начало
    return ''.join(result)

def compress(input_file, encoded_file, decoded_file):
    with open(input_file, 'rb') as f:
        data = f.read()
    
    # Шаг 1: BWT
    bwt_data = bwt_transform(data.decode('utf-8'))

    # Шаг 2: MTF
    mtf_data = move_to_front(bwt_data)

    # Шаг 3: Huffman
    codes, huffman_encoded = huffman_encode(mtf_data)

    # Запись вероятностной модели и закодированных данных в файл
    with open(encoded_file, 'w') as ef:
        ef.write('\n'.join(f"{symbol} = {mtf_data.count(symbol)}" for symbol in codes.keys()) + '\n')  
        ef.write(huffman_encoded)  # Закодированные данные

    # Декодирование
    decoded_mtf = huffman_decode(huffman_encoded, codes)

    # Обратный MTF
    final_data_after_mtf = inverse_move_to_front(decoded_mtf)

    # Обратный BWT
    final_decoded = bwt_inverse(final_data_after_mtf)

    with open(decoded_file, 'wb') as df:
        df.write(final_decoded.encode('utf-8'))

# Пример использования:
compress('input.txt', 'enc.txt', 'dec.txt')