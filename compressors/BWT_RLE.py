from BWT import bwt_transform, bwt_inverse
from RLE import rle_compress, rle_decompress, calc_entropy
import time
import math
import os
from PIL import Image


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


def combined_compress(input_file, compressed_file):
    start_time = time.time()

    # Чтение исходного файла
    with open(input_file, "rb") as f:
        original_data = f.read()

    # Применение BWT
    bwt_data, indices = bwt_transform(original_data)

    # Применение RLE к результату BWT
    compressed_data = rle_compress(bwt_data)

    # Сохранение сжатых данных (индексы BWT + сжатые данные RLE)
    with open(compressed_file, "wb") as f:
        # Сначала записываем количество индексов (4 байта)
        f.write(len(indices).to_bytes(4, 'big'))
        # Затем сами индексы (каждый по 4 байта)
        for idx in indices:
            f.write(idx.to_bytes(4, 'big'))
        # И наконец сжатые данные RLE
        f.write(compressed_data)

    # Вычисление статистики
    original_size = len(original_data)
    compressed_size = len(compressed_data) + 4 + len(indices) * 4  # добавляем размер заголовка с индексами
    ratio = original_size / compressed_size if compressed_size > 0 else 0
    entropy = calc_entropy(original_data)
    avg_len = (compressed_size * 8) / original_size if original_size > 0 else 0

    print(f"Исходный размер: {original_size} байт")
    print(f"Сжатый размер: {compressed_size} байт")
    print(f"Коэффициент сжатия: {ratio:.2f}")
    print(f"Энтропия: {entropy:.2f} бит/символ")
    print(f"Средняя длина кода: {avg_len:.2f} бит/символ")
    print(f"Время сжатия: {time.time() - start_time:.2f} сек")


def combined_decompress(compressed_file, output_file):
    start_time = time.time()

    # Чтение сжатого файла
    with open(compressed_file, "rb") as f:
        # Чтение индексов BWT
        num_indices = int.from_bytes(f.read(4), 'big')
        indices = [int.from_bytes(f.read(4), 'big') for _ in range(num_indices)]
        # Чтение сжатых данных RLE
        rle_data = f.read()

    # Распаковка RLE
    bwt_data = rle_decompress(rle_data)

    # Обратное преобразование BWT
    original_data = bwt_inverse(bwt_data, indices)

    # Сохранение распакованных данных
    with open(output_file, "wb") as f:
        f.write(original_data)

    original_size = len(original_data)
    print(f"декодированный размер: {original_size} байт")
    print(f"Время распаковки: {time.time() - start_time:.2f} сек")


def process_file(input_file, compressed_file, output_file):
    print(f"Сжатие файла {input_file}...")
    combined_compress(input_file, compressed_file)

    print(f"\nРаспаковка файла {compressed_file}...")
    combined_decompress(compressed_file, output_file)


# Пример использования
if __name__ == "__main__":
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


    print("TXT:")
    process_file(file_text, file_coded, decomp_file_txt)

    print("EXE:")
    process_file(file_exe, file_coded, decomp_file_txt)

    img = Image.open(file_bw_img)
    raw_data = JPG_to_RAW(img, raw_filename)
    print("ING_BW:")
    process_file(raw_filename, file_coded, decomp_file_img)

    img = Image.open(file_gray_img)
    raw_data = JPG_to_RAW(img, raw_filename)
    print("IMG_GREY:")
    process_file(raw_filename, file_coded, decomp_file_img)

    img = Image.open(file_color)
    raw_data = JPG_to_RAW(img, raw_filename)
    print("ING_COL:")
    process_file(raw_filename, file_coded, decomp_file_img)

    print("ENWIK:")
    process_file(file_enwik, file_coded, decomp_file_txt)