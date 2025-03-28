import struct
from PIL import Image
import struct

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


def funk_LZ77(S, buffer_size, string_size=256):
    coding_list = []
    N = len(S)
    i = 0
    while i < N:
        # Определяем буфер поиска
        buffer = S[max(0, i - buffer_size):i]
        new_buffer_size = len(buffer)
        shift = -1
        subS = b""

        # Поиск максимального совпадения в буфере
        for j in range(min(string_size, N - i), 0, -1):
            subS = S[i:i + j]
            shift = buffer.rfind(subS)  # Ищем справа налево
            if shift != -1:
                break

        # Если совпадение найдено, добавляем тройку (offset, length, next_byte)
        if shift != -1:
            offset = new_buffer_size - shift
            length = len(subS)
            next_byte = S[i + length:i + length + 1] if i + length < N else b""
            coding_list.append((offset, length, next_byte))
            i += length + 1
        else:
            # Если совпадение не найдено, добавляем (0, 0, next_byte)
            next_byte = S[i:i + 1]
            coding_list.append((0, 0, next_byte))
            i += 1
    return coding_list

def iLZ77(compressed_message):
    S = b""
    for t in compressed_message:
        offset, length, next_byte = t
        N = len(S)
        if offset == 0 and length == 0:
            S += next_byte
        else:
            # Восстанавливаем данные из буфера
            start = N - offset
            S += S[start:start + length] + next_byte
    return S

def calculate_comp(orig_size, comp_size):
    return orig_size / comp_size if comp_size != 0 else 0

def test_compression(data, buffer_sizes):
    original_size = len(data)
    print(f"Размер исходных данных: {original_size} байт")

    results = []
    for buffer_size in buffer_sizes:
        # Кодирование данных
        encoded_data = funk_LZ77(data, buffer_size=buffer_size)

        # Вычисление размера закодированных данных
        comp_size = len(encoded_data) * 7  # Каждая тройка (offset, length, next_byte) занимает 7 байт
        compression = calculate_comp(original_size, comp_size)

        # Сохраняем результаты
        results.append((buffer_size, comp_size, compression))

        # Вывод результатов в консоль
        print(f"Размер буфера: {buffer_size} байт")
        print(f"Размер закодированных данных: {comp_size} байт")
        print(f"Коэффициент сжатия: {compression:.2f}")
        print("-" * 40)
    return results


def write_encoded_to_file(encoded_data, output_file):
    with open(output_file, 'wb') as f:
        for (offset, length, next_byte) in encoded_data:
            f.write(offset.to_bytes(4, byteorder='big'))  # offset как 2 байта
            f.write(length.to_bytes(4, byteorder='big'))    # length как 4 байт
            f.write(next_byte)  # next_byte как 1 байт

def read_encoded_from_file(input_file):
    encoded_data = []
    with open(input_file, 'rb') as f:
        while True:
            offset_bytes = f.read(4)
            if not offset_bytes:
                break
            offset = int.from_bytes(offset_bytes, byteorder='big')
            length_bytes = f.read(4)
            length = int.from_bytes(length_bytes, byteorder='big')
            next_byte = f.read(1)
            encoded_data.append((offset, length, next_byte))
    return encoded_data

"""
# Пример использования
if __name__ == "__main__":
    file1 = "C:/Users/Elizaveta/OneDrive/Документы/для перекида/алгоритмы/homework1/enwik7.txt"
    file2 = "C:/Users/Elizaveta/OneDrive/Документы/для перекида/алгоритмы/homework1/HAdecoded.txt"
   # file3 = "C:/Users/Elizaveta/OneDrive/Документы/для перекида/алгоритмы/homework1/HAdecoded.txt"

    with open(file1, 'rb') as f:
        data = f.read()
    # Размеры буфера для тестирования
    buffer_sizes = [1024, 4096, 16384, 65536, 262144]

    # Проведение экспериментов
    results = test_compression(data, buffer_sizes)

    # Запись закодированных данных в файл

    # Вывод итоговых результатов
    print("\nИтоговые результаты:")
    for buffer_size, compressed_size, compression_ratio in results:
        print(f"Размер буфера: {buffer_size} байт, Коэффициент сжатия: {compression_ratio:.2f}")

    # Чтение закодированных данных из файла
    encoded_data_from_file = read_encoded_from_file(file2)

    # Декодирование
    decoded_data = iLZ77(encoded_data_from_file)

    # Запись декодированных данных в файл

    with open(file3, 'wb') as f:
        f.write(decoded_data)

    print("Кодирование и декодирование текста завершены.")


# Обработка изображения
image_path = "D:/новая папка/PyCharm Community Edition 2024.2.3/sem2Laba1Alg/chernye-kruzhochki.jpg"
raw_filename = "D:/новая папка/PyCharm Community Edition 2024.2.3/sem2Laba1Alg/image.raw"
encoded_image = "D:/новая папка/PyCharm Community Edition 2024.2.3/sem2Laba1Alg/HAcoded.bin"
decoded_raw = "D:/новая папка/PyCharm Community Edition 2024.2.3/sem2Laba1Alg/image_decoded.raw"

# Чтение изображения и преобразование в RAW
img = Image.open(image_path)
raw_data = JPG_to_RAW(img, raw_filename)

# Кодирование RAW-данных
encoded_data = LZ77(raw_data)

# Запись закодированных данных в файл
write_encoded_to_file(encoded_data, encoded_image)

# Чтение закодированных данных из файла
encoded_data_from_file = read_encoded_from_file(encoded_image)

# Декодирование
decoded_data = iLZ77(encoded_data_from_file)

# Запись декодированных данных в файл
with open(decoded_raw, 'wb') as f:
    f.write(decoded_data)

print("Кодирование и декодирование изображения завершены.")
"""
