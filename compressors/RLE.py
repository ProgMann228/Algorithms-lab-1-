import numpy as np
import time
import math
from PIL import Image

import os

def JPG_to_RAW(img,raw_filename):
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

    #print(f"Цветовой режим: {color_mode}, Байтов на пиксель: {bytes_per_pixel}")

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


def count_bytes(data):
    counts = np.zeros(256, dtype=int)
    for byte in data:
        counts[byte] += 1
    return counts

def rle_compress(data):
    result = bytearray()
    i, n = 0, len(data)

    while i < n:
        byte = data[i]
        count = 1

        while i + count < n and count < 255 and data[i + count] == byte:
            count += 1

        if count > 1:
            result.extend([count, byte])
            i += count
        else:
            non_repeat = bytearray()
            while i < n and (i + 1 >= n or data[i] != data[i + 1]):
                non_repeat.append(data[i])
                i += 1
                if len(non_repeat) == 255:
                    break
            # Исправленная строка:
            result.extend([0, len(non_repeat)])
            result.extend(non_repeat)
    return bytes(result)

def rle_decompress(data):
    result = bytearray()
    i, n = 0, len(data)

    while i < n:
        if data[i] == 0:
            length = data[i + 1]
            result.extend(data[i + 2:i + 2 + length])
            i += 2 + length
        else:
            result.extend([data[i + 1]] * data[i])
            i += 2
    return bytes(result)

def calc_entropy(data):
    counts = count_bytes(data)
    total = len(data)
    entropy = 0.0

    for cnt in counts:
        if cnt > 0:
            p = cnt / total
            entropy -= p * math.log2(p)
    return entropy


def process_file(input_file, compressed_file, decompressed_file):
    start = time.time()
    try:
        with open(input_file, "rb") as f:
            original = f.read()
    except FileNotFoundError:
        print(f"Файл {input_file} не найден!")
        return

    compressed = rle_compress(original)

    with open(compressed_file, "wb") as f:
        f.write(compressed)

    decompressed = rle_decompress(compressed)

    with open(decompressed_file, "wb") as f:
        f.write(decompressed)

    entropy = calc_entropy(original)
    original_size = os.path.getsize(input_file) * 8  # В битах
    compressed_size = os.path.getsize(compressed_file) * 8  # В битах
    decoded = os.path.getsize(decompressed_file) * 8  # В битах
    compression = original_size / compressed_size

    print(f"\nКоэффициент сжатия: {compression:.2f}")
    print(f"размер исходного: {original_size:.2f}")
    print(f"размер раскодированного: {decoded:.2f}")
    print(f"Сжатый размер: {len(compressed)} байт")

    print(f"Энтропия: {entropy:.2f} бит/символ")

"""

file_text = "D:/новая папка/PyCharm Community Edition 2024.2.3/sem2Laba1Alg/Приключения Незнайки.txt"
file_enwik = "C:/Users/User/OneDrive/Документы/алгоритмы вуз/homework1/enwik9/enwik7.txt"
file_exe = "C:/Users/User/OneDrive/Документы/алгоритмы вуз/homework1/aitstatic.exe"
file_bw_img = "C:/Users/User/OneDrive/Документы/алгоритмы вуз/homework1/chernye-kruzhochki.jpg"
file_gray_img = "C:/Users/User/OneDrive/Документы/алгоритмы вуз/homework1/Adams_The_Tetons_and_the_Snake_River.jpg"
file_color = "C:/Users/User/OneDrive/Документы/алгоритмы вуз/homework1/AAA.jpg"
raw_filename = "D:/новая папка/PyCharm Community Edition 2024.2.3/sem2Laba1Alg/image.raw"
file_coded = "D:/новая папка/PyCharm Community Edition 2024.2.3/sem2Laba1Alg/HAcoded.bin"
decomp_file_txt = "decompressed.txt"
decomp_file_img = "decompressed.raw"

process_file(file_text, file_coded, decomp_file_txt)

process_file(file_exe, file_coded, decomp_file_txt)

img = Image.open(file_bw_img)
raw_data = JPG_to_RAW(img, raw_filename)
process_file(raw_filename, file_coded, decomp_file_img)

img = Image.open(file_gray_img)
raw_data = JPG_to_RAW(img, raw_filename)
process_file(raw_filename, file_coded, decomp_file_img)

img = Image.open(file_color)
raw_data = JPG_to_RAW(img, raw_filename)
process_file(raw_filename, file_coded, decomp_file_img)

process_file(file_enwik, file_coded, decomp_file_txt)
"""