import struct
from PIL import Image
import struct
import os

import struct
from collections import defaultdict

MAX_DICT_SIZE = 65536  # Максимальный размер словаря

#преобразование изображения в raw формат

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
    return raw_data


def lz78_encode(input_file, output_file):
    with open(input_file, 'rb') as f:
        data = f.read()

    dictionary = {b'': 0}
    next_code = 1
    current = b''
    encoded = []
    CS = 4  # Фиксированный размер кода - 4 байта (максимум 4,294,967,295 записей)

    for byte in data:
        current += bytes([byte])
        if current not in dictionary:
            dictionary[current] = next_code
            next_code += 1
            prefix = current[:-1]
            encoded.append((dictionary.get(prefix, 0), bytes([byte])))
            current = b''

    if current:
        prefix = dictionary.get(current[:-1], 0)
        last_byte = current[-1:]
        encoded.append((prefix, last_byte))

    with open(output_file, 'wb') as f:
        for code, byte in encoded:
            f.write(code.to_bytes(CS, byteorder='big'))
            f.write(byte)

    original_size = os.path.getsize(input_file)
    compressed_size = os.path.getsize(output_file)
    print(f"Оригинальный размер: {original_size} байт")
    print(f"Сжатый размер: {compressed_size} байт")
    print(f"Коэффициент сжатия: {original_size / compressed_size:.2f}")


def lz78_decode(input_file, output_file):
    with open(input_file, 'rb') as f:
        data = f.read()

    dictionary = {0: b''}
    next = 1
    decoded = []
    i = 0
    CS = 4  # Должно совпадать с кодировщиком

    while i < len(data):
        code = int.from_bytes(data[i:i + CS], byteorder='big')
        byte = data[i + CS:i + CS + 1]
        i += CS + 1

        entry = dictionary.get(code, b'') + byte
        decoded.append(entry)
        dictionary[next] = entry
        next += 1

    with open(output_file, 'wb') as f:
        f.write(b''.join(decoded))

    decompressed_size = os.path.getsize(output_file)
    print(f"Декомпрессия размер: {decompressed_size}")



file_text = "C:/Users/Elizaveta/OneDrive/Документы/для перекида/алгоритмы/homework1/Приключения Незнайки.txt"
file_enwik="C:/Users/Elizaveta/OneDrive/Документы/для перекида/алгоритмы/homework1/enwik7.txt"
file_exe="C:/Users/Elizaveta/OneDrive/Документы/для перекида/алгоритмы/homework1/vmwp.exe"
file_bw_img="C:/Users/Elizaveta/OneDrive/Документы/для перекида/алгоритмы/homework1/chernye-kruzhochki.jpg"
file_gray_img="C:/Users/Elizaveta/OneDrive/Документы/для перекида/алгоритмы/homework1/gray_image.png"
file_color="C:/Users/Elizaveta/OneDrive/Документы/для перекида/алгоритмы/homework1/color_image.png"
raw_filename = "C:/Users/Elizaveta/OneDrive/Документы/для перекида/алгоритмы/homework1/image.raw"
file_coded = "C:/Users/Elizaveta/OneDrive/Документы/для перекида/алгоритмы/homework1/HAcoded_№2.bin"
decomp_file_txt = "decompressed.txt"
decomp_file_img = "decompressed.raw"

print("TXT:")
lz78_encode(file_text, file_coded)
lz78_decode(file_coded, decomp_file_txt)

print("EXE:")
lz78_encode(file_exe, file_coded)
lz78_decode(file_coded, decomp_file_txt)

print("ING_BW:")
img = Image.open(file_bw_img)
raw_data = JPG_to_RAW(img, raw_filename)
lz78_encode(raw_filename, file_coded)
lz78_decode(file_coded, decomp_file_img)

print("ING_GREY:")
img = Image.open(file_gray_img)
raw_data = JPG_to_RAW(img, raw_filename)
lz78_encode(raw_filename, file_coded)
lz78_decode(file_coded, decomp_file_img)

print("ING_COL:")
img = Image.open(file_color)
raw_data = JPG_to_RAW(img, raw_filename)
lz78_encode(raw_filename, file_coded)
lz78_decode(file_coded, decomp_file_img)

print("ENWIK:")
lz78_encode(file_enwik, file_coded)
lz78_decode(file_coded, decomp_file_txt)