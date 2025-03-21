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

    for i in range(128):
        if C[i] != 0:
            leaf = Node(symbol=chr(i), counter=C[i])
            Q.put(leaf)

    while Q.qsize() > 1:
        left = Q.get()
        right = Q.get()
        merged = Node(counter=left.counter + right.counter)
        merged.left = left
        merged.right = right
        Q.put(merged)

    return Q.get() 

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
        coded_message += codebook[s]
    padding_len = 8 - (len(coded_message) % 8)
    if padding_len != 8:
        coded_message += '0' * padding_len
    return codebook, coded_message, padding_len


def huffman_decode(coded_message, codebook, padding_len):
    reverse_codebook = {v: k for k, v in codebook.items()}
    if padding_len != 8:
      coded_message = coded_message[:-padding_len]
    current_code = ''
    decoded_str = ''

    for bit in coded_message:
        current_code += bit
        if current_code in reverse_codebook:
            decoded_str += reverse_codebook[current_code]
            current_code = ''

    return decoded_str

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(data)

def main(input_file, encoded_output_file, decoded_output_file):
    input_string = read_file(input_file)

    codebook, encoded, padding_len = huffman_encode(input_string)

    encoded_output = []
    for symbol, count in codebook.items():
        encoded_output.append(f"{symbol} = {input_string.count(symbol)}")
    encoded_output.append(encoded) 
    write_file(encoded_output_file, '\n'.join(encoded_output))


    encoded_lines = read_file(encoded_output_file).split('\n')
    read_codebook = {}
    read_padding_len = 8  
    read_encoded = ""

    for i, line in enumerate(encoded_lines):
        if '=' in line:  # Frequency lines
            symbol, count = line.split(' = ')
            read_codebook[symbol] = count
        else:
            read_encoded = line
            break

    decoded = huffman_decode(read_encoded, codebook, padding_len)


    write_file(decoded_output_file, decoded)

if __name__ == "__main__":
    main('input.txt', 'encoded_output.txt', 'decoded_output.txt')