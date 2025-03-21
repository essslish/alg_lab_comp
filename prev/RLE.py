def RLE(data_input):
    encoding = bytearray()
    count = 1
    if not data_input:
        return encoding
    for i in range(1, len(data_input)):
        if data_input[i] == data_input[i - 1]:
            count += 1
        else:
            if count == 1:
                encoding.extend(str(count).encode()) 
                encoding.append(data_input[i - 1])
            else:
                encoding.extend(str(count).encode())
                encoding.append(data_input[i - 1])
            count = 1
    else:
        if count == 1:
            encoding.extend(str(count).encode()) 
            encoding.append(data_input[i])
        else:
            encoding.extend(str(count).encode())
            encoding.append(data_input[i])
    return encoding

def RLE_REV(data_output):
    decoding = bytearray()
    count = ''
    for char in data_output.decode():
        if char.isdigit():
            count += char
        else:
            decoding.extend([ord(char)] * int(count))
            count = ''
    return decoding

def compress(input_file, compressed_file):
    with open(input_file, 'rb') as file:
        data = file.read()
    compressed_data = RLE(data)
    with open(compressed_file, 'wb') as file:
        file.write(compressed_data)

def decompress(compressed_file, output_filename):
    with open(compressed_file, 'rb') as file:
        data = file.read()
    decompressed_data = RLE_REV(data)
    with open(output_filename, 'wb') as file:
        file.write(decompressed_data)

input_file = 'input.txt'
compressed_file = 'compressed.txt'
decompressed_file = 'decompressed.txt'

compress(input_file, compressed_file)

decompress(compressed_file, decompressed_file)


with open(decompressed_file, 'r') as file:
    print(file.read())  
