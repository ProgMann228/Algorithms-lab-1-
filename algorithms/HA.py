
import heapq
from PIL import Image
import numpy as np
from collections import Counter, namedtuple
import os

#преобразование изображения в raw формат
def PNG_to_RAW(img,raw_filename):
    # Определяем цветовую глубину
    if img.mode == "1":  # Чёрно-белое (1 бит на пиксель)
        color_mode = "binary"
        bytes_per_pixel = 1 / 8  # 1 бит = 1/8 байта
    elif img.mode == "L":  # Оттенки серого (8 бит на пиксель)
        color_mode = "grayscale"
        bytes_per_pixel = 1  # 1 байт на пиксель
    elif img.mode == "RGB":  # Цветное (24 бита = 3 байта на пиксель)
        color_mode = "color"
        bytes_per_pixel = 3
    else:
        raise ValueError(f"Неподдерживаемый режим: {img.mode}")

    print(f"Цветовой режим: {color_mode}, Байтов на пиксель: {bytes_per_pixel}")

    raw_data = bytearray() #для хранения набора байтов

    # повторное преобраз-е на случай если попался формат который обошел проверку
    if color_mode == "binary":
        img = img.convert("1")
    elif color_mode == "grayscale":
        img = img.convert("L")
    elif color_mode == "color":
        img = img.convert("RGB")

    # Записываем пиксели в список
    pixels = list(img.getdata()) #он выглядит так [(255, 0, 0), (0, 255, 0)]

    for pixel in pixels:
        if isinstance(pixel, tuple):  # RGB
            raw_data.extend(pixel)  # Добавляем три байта (R, G, B)
        else:  # Градации серого или ЧБ
            raw_data.append(pixel)

    print(f"Размер необработанных данных: {len(raw_data)} байт")

    #сохраняем поток байтов в файл
    #with as гарантирует автоматическое закрытие файла
    with open(raw_filename, "wb") as raw_file:
        raw_file.write(raw_data)



class Node:
    def __init__(self, char: int, freq, left=None, right=None, par=None):
        self.char = char  # Байтовый символ (0-255)
        self.freq = freq  # Частота символа
        self.left = left  # Левый потомок
        self.right = right  # Правый потомок
        self.par = par  # Родитель

    def __lt__(self, other):
        return self.freq < other.freq  # Сравниваем по частоте


def heapify(fr, n, i):
    smallest = i
    l = 2 * i + 1
    r = 2 * i + 2
    if l < n and fr[l].freq < fr[smallest].freq:
        smallest = l
    if r < n and fr[r].freq < fr[smallest].freq:
        smallest = r

    if smallest != i:
        fr[i], fr[smallest] = fr[smallest], fr[i]
        heapify(fr, n, smallest)


def build_min_heap(fr):
    n = len(fr)
    root = n // 2 - 1
    for i in range(root, -1, -1):
        heapify(fr, n, i)
    return fr


def extract_min(heap):
    if len(heap) == 0:
        return None  # Куча пуста

    root = heap[0]
    heap[0] = heap[-1]  #
    heap.pop()  # Удаляем последний элемент

    heapify(heap, len(heap), 0)

    return root


def insert(heap, element):
    heap.append(element)
    i = len(heap) - 1
    parent = (i - 1) // 2

    # Поднимаем элемент вверх, если он меньше родителя
    while i > 0 and heap[i].freq < heap[parent].freq:
        heap[i], heap[parent] = heap[parent], heap[i]
        i = parent
        parent = (i - 1) // 2  # Обновляем родителя
    return heap


def Haffman_tree(heap):
    while len(heap) > 1:
        left = extract_min(heap)
        right = extract_min(heap)

        # Создаем новый узел, объединяя два самых редких символа
        parent = Node(None, left.freq + right.freq, left, right)
        #print(parent.freq)
        heap = insert(heap, parent)
    return heap[0]


def HA_codes(node, cur='', codes=None):
    if codes is None:
        codes = {}  # словарь

    if node.char is not None:  # узел является листом (1 символ)
        codes[node.char] = cur
    else:
        if node.left:
            HA_codes(node.left, cur + '0', codes)
        if node.right:
            HA_codes(node.right, cur + '1', codes)

    return codes


# Функция преобразования битовой строки в байты
def bits_to_bytes(bit_string):
    padding = 8 - (len(bit_string) % 8)
    bit_string = f"{padding:08b}" + bit_string + '0' * padding
    byte_array = bytearray(int(bit_string[i:i + 8], 2) for i in range(0, len(bit_string), 8))
    return bytes(byte_array)

# Функция преобразования байтов обратно в битовую строку
def bytes_to_bits(byte_data):
    bit_string = ''.join(f"{byte:08b}" for byte in byte_data)
    padding = int(bit_string[:8], 2)
    return bit_string[8:-padding] if padding > 0 else bit_string[8:]


# Кодирование файла (txt, bin, raw)
def encode_file(input_file, output_file):
    with open(input_file, "rb") as file:
        data = file.read()
    frequencies = [Node(byte, freq) for byte, freq in Counter(data).items()]
    heap = build_min_heap(frequencies)
    encoded = HA_codes(Haffman_tree(heap))
    encoded_bits = ''.join(encoded[byte] for byte in data)
    compressed_data = bits_to_bytes(encoded_bits)
    with open(output_file, "wb") as file:
        file.write(compressed_data)


# Декодирование файла
def decode_file(input_file, output_file, huffman_tree):
    with open(input_file, "rb") as file:
        encoded_data = file.read()
    bit_string = bytes_to_bits(encoded_data)
    decoded_data = []
    current_node = huffman_tree
    for bit in bit_string:
        current_node = current_node.left if bit == '0' else current_node.right
        if current_node.char is not None:
            decoded_data.append(current_node.char)
            current_node = huffman_tree
    with open(output_file, "wb") as file:
        file.write(bytearray(decoded_data))
"""
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
encode_file(file_text, file_coded)
decode_file(file_coded, decomp_file_txt, Haffman_tree(build_min_heap([Node(byte, freq) for byte, freq in Counter(open(file_text, 'rb').read()).items()])))

original_size = os.path.getsize(file_text) * 8  # В битах
compressed_size = os.path.getsize(file_coded) *8  # В битах
decoded=os.path.getsize(decomp_file_txt) * 8  # В битах
compression = original_size / compressed_size

print(f"Коэффициент сжатия: {compression:.2f}")
print(f"размер исходного: {original_size:.2f}")
print(f"размер раскодированного: {decoded:.2f}")


print("EXE:")
encode_file(file_exe, file_coded)
decode_file(file_coded, decomp_file_txt, Haffman_tree(build_min_heap([Node(byte, freq) for byte, freq in Counter(open(file_exe, 'rb').read()).items()])))

original_size = os.path.getsize(file_exe) * 8  # В битах
compressed_size = os.path.getsize(file_coded) *8  # В битах
decoded=os.path.getsize(decomp_file_txt) * 8  # В битах
compression = original_size / compressed_size

print(f"Коэффициент сжатия: {compression:.2f}")
print(f"размер исходного: {original_size:.2f}")
print(f"размер раскодированного: {decoded:.2f}")


img = Image.open(file_bw_img)
raw_data = PNG_to_RAW(img, raw_filename)
print("ING_BW:")
encode_file(raw_filename, file_coded)
decode_file(file_coded, decomp_file_img, Haffman_tree(build_min_heap([Node(byte, freq) for byte, freq in Counter(open(raw_filename, 'rb').read()).items()])))

original_size = os.path.getsize(raw_filename) * 8  # В битах
compressed_size = os.path.getsize(file_coded) *8  # В битах
decoded=os.path.getsize(decomp_file_img) * 8  # В битах
compression = original_size / compressed_size

print(f"Коэффициент сжатия: {compression:.2f}")
print(f"размер исходного: {original_size:.2f}")
print(f"размер раскодированного: {decoded:.2f}")


img = Image.open(file_gray_img)
raw_data = PNG_to_RAW(img, raw_filename)
print("IMG_GREY:")
encode_file(raw_filename, file_coded)
decode_file(file_coded, decomp_file_img, Haffman_tree(build_min_heap([Node(byte, freq) for byte, freq in Counter(open(raw_filename, 'rb').read()).items()])))

original_size = os.path.getsize(raw_filename) * 8  # В битах
compressed_size = os.path.getsize(file_coded) *8  # В битах
decoded=os.path.getsize(decomp_file_img) * 8  # В битах
compression = original_size / compressed_size

print(f"Коэффициент сжатия: {compression:.2f}")
print(f"размер исходного: {original_size:.2f}")
print(f"размер раскодированного: {decoded:.2f}")


img = Image.open(file_color)
raw_data = PNG_to_RAW(img, raw_filename)
print("ING_COL:")
encode_file(raw_filename, file_coded)
decode_file(file_coded, decomp_file_img, Haffman_tree(build_min_heap([Node(byte, freq) for byte, freq in Counter(open(raw_filename, 'rb').read()).items()])))

original_size = os.path.getsize(raw_filename) * 8  # В битах
compressed_size = os.path.getsize(file_coded) *8  # В битах
decoded=os.path.getsize(decomp_file_img) * 8  # В битах
compression = original_size / compressed_size

print(f"Коэффициент сжатия: {compression:.2f}")
print(f"размер исходного: {original_size:.2f}")
print(f"размер раскодированного: {decoded:.2f}")


print("ENWIK:")
encode_file(file_enwik, file_coded)
decode_file(file_coded, decomp_file_txt, Haffman_tree(build_min_heap([Node(byte, freq) for byte, freq in Counter(open(file_enwik, 'rb').read()).items()])))

original_size = os.path.getsize(file_enwik) * 8  # В битах
compressed_size = os.path.getsize(file_coded) *8  # В битах
decoded=os.path.getsize(decomp_file_txt) * 8  # В битах
compression = original_size / compressed_size

print(f"Коэффициент сжатия: {compression:.2f}")
print(f"размер исходного: {original_size:.2f}")
print(f"размер раскодированного: {decoded:.2f}")
"""





