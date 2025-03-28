from PIL import Image
import os


# Открываем изображение
image_path = "C:/Users/Elizaveta/OneDrive/Документы/для перекида/алгоритмы/homework1/Adams_The_Tetons_and_the_Snake_River.jpg"
img = Image.open(image_path)

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
raw_filename = "C:/Users/Elizaveta/OneDrive/Документы/для перекида/алгоритмы/homework1/image.raw"
#with as гарантирует автоматическое закрытие файла
with open(raw_filename, "wb") as raw_file:
    raw_file.write(raw_data)

print(f"RAW-файл сохранён как {raw_filename}")

original_size = os.path.getsize(image_path)
raw_size = os.path.getsize(raw_filename)

print(f"Размер оригинального файла: {original_size} байт")
print(f"Размер RAW-файла: {raw_size} байт")

compression_ratio = original_size / raw_size
print(f"Коэффициент сжатия: {compression_ratio:.2f}")