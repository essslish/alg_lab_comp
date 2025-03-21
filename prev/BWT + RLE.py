def bwt_transform(data):
    n = len(data)
    shifts = [data[i:] + data[:i] for i in range(n)]
    
    # Сортировка сдвигов
    sorted_shifts = sorted(shifts)
    
    # Получение последнего столбца для BWT
    last_column = ''.join(shift[-1] for shift in sorted_shifts)
    return last_column

def bwt_inverse(last_column):
    n = len(last_column)
    table = [''] * n
    for _ in range(n):
        # Сортировка таблицы по последнему символу
        table = sorted(last_column[i] + table[i] for i in range(n))
    return table[0]

def RLE(data_input):
    """Сжатие данных методом RLE."""
    encoding = []
    if not data_input:
        return encoding
    count = 1
    for i in range(1, len(data_input)):
        if data_input[i] == data_input[i - 1]:
            count += 1
        else:
            encoding.append(str(count))
            encoding.append(data_input[i - 1])
            count = 1
    # Добавляем последний символ
    encoding.append(str(count))
    encoding.append(data_input[-1])
    return ''.join(encoding)

def RLE_REV(data_output):
    """Декомпрессия данных методом RLE."""
    decoding = []
    count = ''
    for char in data_output:
        if char.isdigit():
            count += char
        else:
            decoding.extend([char] * int(count))
            count = ''
    return ''.join(decoding)

def compress(input_file, compressed_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        data = file.read().strip()
    
    # Применяем BWT
    bwt_data = bwt_transform(data)
    # Применяем RLE
    compressed_data = RLE(bwt_data)
    
    with open(compressed_file, 'w', encoding='utf-8') as file:
        file.write(compressed_data)

def decompress(compressed_file, output_filename):
    with open(compressed_file, 'r', encoding='utf-8') as file:
        data = file.read()
    
    # Раскодируем RLE
    rle_decoded_data = RLE_REV(data)
    # Применяем обратное BWT
    decompressed_data = bwt_inverse(rle_decoded_data)
    
    with open(output_filename, 'w', encoding='utf-8') as file:
        file.write(decompressed_data)

# Путь к файлам
input_file = 'input.txt'
compressed_file = 'comp.txt'
decompressed_file = 'decomp.txt'

# Сжатие файла
compress(input_file, compressed_file)

# Расшифровка файла
decompress(compressed_file, decompressed_file)

# Проверка результатов
with open(decompressed_file, 'r', encoding='utf-8') as file:
    print(file.read())  