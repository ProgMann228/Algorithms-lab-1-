import struct
from PIL import Image
import struct
import os


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


def MTF(stroka):
    T = bytearray(range(256))  # Алфавит из 256 байтов (0-255)
    encoded = bytearray()

    for byte in stroka:
        i = T.index(byte)  # Находим индекс байта
        encoded.append(i)
        T.insert(0, T.pop(i))  # Перемещаем байт в начало

    return bytes(encoded)

# Обратное преобразование
def iMTF(coded_stroka):
    T = bytearray(range(256))  # Восстанавливаем тот же алфавит
    decoded = bytearray()

    for i in coded_stroka:
        byte = T[i]
        decoded.append(byte)
        T.insert(0, T.pop(i))  # Перемещаем байт в начало

    return bytes(decoded)

"""
file_text = "C:/Users/Elizaveta/OneDrive/Документы/для перекида/алгоритмы/homework1/Руководство.txt"
#file_enwik
file_exe="C:/Users/Elizaveta/OneDrive/Документы/для перекида/алгоритмы/homework1/aitstatic.exe"
file_bw_img="C:/Users/Elizaveta/OneDrive/Документы/для перекида/алгоритмы/homework1/chernye-kruzhochki.jpg"
file_gray_img="C:/Users/Elizaveta/OneDrive/Документы/для перекида/алгоритмы/homework1/Adams.jpg"
file_color="C:/Users/Elizaveta/OneDrive/Документы/для перекида/алгоритмы/homework1/IMG_3405.jpg"
raw_filename = "C:/Users/Elizaveta/OneDrive/Документы/для перекида/алгоритмы/homework1/image.raw"

file_coded = "C:/Users/Elizaveta/OneDrive/Документы/для перекида/алгоритмы/homework1/HAcoded.bin"
file_decoded = "C:/Users/Elizaveta/OneDrive/Документы/для перекида/алгоритмы/homework1/HAdecoded.txt"

#для txt, bin
def Text(data,file1,file2,file3):
    encoded = MTF(data)
    with open(file2, 'wb') as f:
        f.write(bytes(encoded))

    # Читаем закодированные данные
    with open(file2, "rb") as file:
        encoded_data = file.read()

    # Декодирование данных
    decoded_data = iMTF(encoded_data)
    # Сохранение декодированных данных
    with open(file3, 'wb') as f:
        f.write(decoded_data)
    original_size = os.path.getsize(file1) * 8  # В битах
    compressed_size = os.path.getsize(file2) * 8  # В битах

    decoded = os.path.getsize(file3) * 8  # В битах
    compression = original_size / compressed_size

    print(f"Коэффициент сжатия: {compression:.2f}")
    print(f"размер исходного: {original_size:.2f}")
    print(f"размер закодированного: {compressed_size:.2f}")
    print(f"размер раскодированного: {decoded:.2f}")
    print("-"*30)



with open(file_text, "rb") as file:
    data = file.read()
print("TXT:")
Text(data,file_text,file_coded,file_decoded)

with open(file_exe, "rb") as file:
    data = file.read()
print("EXE:")
Text(data,file_exe,file_coded,file_decoded)

img = Image.open(file_bw_img)
raw_data = JPG_to_RAW(img, raw_filename)
print("ING_BW:")
Text(raw_data,raw_filename,file_coded,file_decoded)

img = Image.open(file_gray_img)
raw_data = JPG_to_RAW(img, raw_filename)
print("IMG_GR:")
Text(raw_data,raw_filename,file_coded,file_decoded)

img = Image.open(file_color)
raw_data = JPG_to_RAW(img, raw_filename)
print("IMG_COL:")
Text(raw_data,raw_filename,file_coded,file_decoded)


print("Кодирование и декодирование завершены.")
"""