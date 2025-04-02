import os
from collections import Counter
from PIL import Image

from LZ78 import lz78_encode, lz78_decode
from HA import encode_file, decode_file, Haffman_tree, build_min_heap, Node ,\
    bits_to_bytes,bytes_to_bits,HA_codes,PNG_to_RAW


def combined_compress(input_file, output_file):
    """Сжимает файл, используя сначала LZ78, затем алгоритм Хаффмана"""
    # Временный файл для LZ78
    temp_lz_file = "temp_lz78.bin"

    # 1. Сжимаем LZ78
    lz78_encode(input_file, temp_lz_file)

    # 2. Подготовка к Хаффману
    with open(temp_lz_file, "rb") as f:
        data = f.read()

    # Считаем частоту байтов
    freq = Counter(data)
    # Создаем узлы для дерева
    nodes = [Node(byte, count) for byte, count in freq.items()]

    # Строим дерево Хаффмана
    heap = build_min_heap(nodes)
    huffman_tree = Haffman_tree(heap)
    codes = HA_codes(huffman_tree)

    # Кодируем данные
    bits = ''.join([codes[byte] for byte in data])
    compressed = bits_to_bytes(bits)

    # Сохраняем результат
    with open(output_file, "wb") as f:
        f.write(compressed)

    # Удаляем временный файл
    os.remove(temp_lz_file)

    # Выводим статистику
    orig_size = os.path.getsize(input_file)
    comp_size = os.path.getsize(output_file)
    print(f"Исходный размер: {orig_size} байт")
    print(f"После сжатия: {comp_size} байт")
    print(f"Коэффициент сжатия: {orig_size / comp_size:.2f}")

    return huffman_tree


def combined_decompress(input_file, output_file, huffman_tree):
    """Распаковывает файл, сжатый combined_compress"""
    # Временный файл для Хаффмана
    temp_huff_file = "temp_huffman.bin"

    # 1. Читаем сжатые данные
    with open(input_file, "rb") as f:
        compressed = f.read()

    # 2. Декодируем Хаффмана
    bits = bytes_to_bits(compressed)
    decoded = []
    current_node = huffman_tree

    for bit in bits:
        if bit == '0':
            current_node = current_node.left
        else:
            current_node = current_node.right

        if current_node.char is not None:
            decoded.append(current_node.char)
            current_node = huffman_tree

    # Сохраняем временный файл для LZ78
    with open(temp_huff_file, "wb") as f:
        f.write(bytearray(decoded))

    # 3. Декодируем LZ78
    lz78_decode(temp_huff_file, output_file)

    # Удаляем временный файл
    os.remove(temp_huff_file)

    print(f"Размер после распаковки: {os.path.getsize(output_file)} байт")

file_text = "C:/Users/Elizaveta/OneDrive/Документы/для перекида/алгоритмы/homework1/Приключения Незнайки.txt"
file_enwik="C:/Users/Elizaveta/OneDrive/Документы/для перекида/алгоритмы/homework1/enwik7.txt"
file_exe="C:/Users/Elizaveta/OneDrive/Документы/для перекида/алгоритмы/homework1/Windows Notepad Installer.exe"
file_bw_img="C:/Users/Elizaveta/OneDrive/Документы/для перекида/алгоритмы/homework1/chernye-kruzhochki.jpg"
file_gray_img="C:/Users/Elizaveta/OneDrive/Документы/для перекида/алгоритмы/homework1/Adams.jpg"
file_color="C:/Users/Elizaveta/OneDrive/Документы/для перекида/алгоритмы/homework1/color_image.png"
raw_filename = "C:/Users/Elizaveta/OneDrive/Документы/для перекида/алгоритмы/homework1/image.raw"
file_coded = "C:/Users/Elizaveta/OneDrive/Документы/для перекида/алгоритмы/homework1/HAcoded_№2.bin"
decomp_file_txt = "decompressed.txt"
decomp_file_img = "decompressed.raw"


print("TXT:")
huffman_tree = combined_compress(file_text, file_coded)
combined_decompress(file_coded, decomp_file_txt, huffman_tree)

print("EXE:")
huffman_tree = combined_compress(file_exe, file_coded)
combined_decompress(file_coded, decomp_file_txt, huffman_tree)

print("ING_BW:")
img = Image.open(file_bw_img)
raw_data = PNG_to_RAW(img, raw_filename)
huffman_tree = combined_compress(raw_filename, file_coded)
combined_decompress(file_coded, decomp_file_img, huffman_tree)

print("ING_GREY:")
img = Image.open(file_gray_img)
raw_data = PNG_to_RAW(img, raw_filename)
huffman_tree = combined_compress(raw_filename, file_coded)
combined_decompress(file_coded, decomp_file_img, huffman_tree)

print("ING_COL:")
img = Image.open(file_color)
raw_data = PNG_to_RAW(img, raw_filename)
huffman_tree = combined_compress(raw_filename, file_coded)
combined_decompress(file_coded, decomp_file_img, huffman_tree)

print("ENWIK:")
huffman_tree = combined_compress(file_enwik, file_coded)
combined_decompress(file_coded, decomp_file_txt, huffman_tree)