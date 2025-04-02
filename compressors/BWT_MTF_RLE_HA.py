from BWT_MTF import compress as bwt_mtf_compress, decompress as bwt_mtf_decompress
from HA import encode_file as ha_encode, decode_file as ha_decode, Node, Haffman_tree, \
    build_min_heap, Counter, PNG_to_RAW
from PIL import Image
import os


def rle_compress(data):
    """Функция RLE-сжатия (аналогичная той, что в вашем RLE модуле)"""
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
            result.extend([0, len(non_repeat)])
            result.extend(non_repeat)
    return bytes(result)


def rle_decompress(data):
    """Функция RLE-распаковки"""
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


def full_compress(input_file, bwt_mtf_comp, rle_comp, comp_file):
    """Полное сжатие: BWT -> MTF -> RLE -> Хаффман"""
    # Шаг 1: BWT + MTF
    print("Применяем BWT + MTF...")
    bwt_mtf_compress(input_file, bwt_mtf_comp, block_size=1024)

    # Шаг 2: Читаем BWT+MTF результат и применяем RLE
    print("Применяем RLE...")
    with open(bwt_mtf_comp, "rb") as f:
        bwt_mtf_data = f.read()
    rle_data = rle_compress(bwt_mtf_data)
    with open(rle_comp, "wb") as f:
        f.write(rle_data)

    # Шаг 3: Хаффман
    print("Применяем кодирование Хаффмана...")
    ha_encode(rle_comp, comp_file)

    # Вывод информации о сжатии
    original_size = os.path.getsize(input_file)
    compressed_size = os.path.getsize(comp_file)
    print(f"\nИсходный размер: {original_size} байт")
    print(f"Сжатый размер: {compressed_size} байт")
    print(f"Коэффициент сжатия: {original_size / compressed_size:.2f}")


def full_decompress(bwt_mtf_comp, rle_comp, comp_file, dec_HA, dec_file):
    """Полная декомпрессия: Хаффман -> RLE -> MTF -> BWT"""
    # Шаг 1: Декодирование Хаффмана
    print("\nДекодируем Хаффман...")
    with open(rle_comp, "rb") as f:
        data = f.read()

    freq = Counter(data)
    nodes = [Node(byte, count) for byte, count in freq.items()]
    huffman_tree = Haffman_tree(build_min_heap(nodes))

    # Шаг 2: RLE декомпрессия
    print("Декодируем RLE...")
    with open(dec_HA, "rb") as f:
        rle_data = f.read()
    bwt_mtf_data = rle_decompress(rle_data)
    with open(bwt_mtf_comp, "wb") as f:
        f.write(bwt_mtf_data)

    # Шаг 3: Обратное MTF + BWT
    print("Применяем обратное MTF + BWT...")
    bwt_mtf_decompress(bwt_mtf_comp, dec_file)

    # Проверка целостности
    decompressed_size = os.path.getsize(dec_file)
    print(f"\nРазмер после декомпрессии: {decompressed_size} байт")


if __name__ == "__main__":
    file_text = "D:/новая папка/PyCharm Community Edition 2024.2.3/sem2Laba1Alg/Приключения Незнайки.txt"
    file_enwik = "C:/Users/User/OneDrive/Документы/алгоритмы вуз/homework1/enwik9/enwik7.txt"
    file_exe = "C:/Users/User/OneDrive/Документы/алгоритмы вуз/homework1/aitstatic.exe"
    file_bw_img = "C:/Users/User/OneDrive/Документы/алгоритмы вуз/homework1/chernye-kruzhochki.jpg"
    file_gray_img = "C:/Users/User/OneDrive/Документы/алгоритмы вуз/homework1/Adams_The_Tetons_and_the_Snake_River.jpg"
    file_color = "C:/Users/User/OneDrive/Документы/алгоритмы вуз/homework1/AAA.jpg"
    raw_filename = "D:/новая папка/PyCharm Community Edition 2024.2.3/sem2Laba1Alg/image.raw"

    temp_bwt_mtf = "temp_bwt_mtf.bin"
    temp_rle = "temp_rle.bin"
    file_coded = "D:/новая папка/PyCharm Community Edition 2024.2.3/sem2Laba1Alg/HAcoded.bin"
    decomp_file_txt = "decompressed.txt"
    decomp_file_img = "decompressed.raw"
    temp_dec_ha = "temp_decode_ha.bin"

    print("ENWIK:")
    full_compress(file_enwik, temp_bwt_mtf, temp_rle, file_coded)
    full_decompress(temp_bwt_mtf, temp_rle, file_coded, temp_dec_ha, decomp_file_txt)

    print("TXT:")
    full_compress(file_text, temp_bwt_mtf, temp_rle, file_coded)
    full_decompress(temp_bwt_mtf, temp_rle, file_coded, temp_dec_ha, decomp_file_txt)

    print("EXE:")
    full_compress(file_exe, temp_bwt_mtf, temp_rle, file_coded)
    full_decompress(temp_bwt_mtf, temp_rle, file_coded, temp_dec_ha, decomp_file_txt)

    img = Image.open(file_bw_img)
    raw_data = PNG_to_RAW(img, raw_filename)
    print("ING_BW:")
    full_compress(raw_filename, temp_bwt_mtf, temp_rle, file_coded)
    full_decompress(temp_bwt_mtf, temp_rle, file_coded, temp_dec_ha, decomp_file_img)

    img = Image.open(file_gray_img)
    raw_data = PNG_to_RAW(img, raw_filename)
    print("IMG_GREY:")
    full_compress(raw_filename, temp_bwt_mtf, temp_rle, file_coded)
    full_decompress(temp_bwt_mtf, temp_rle, file_coded, temp_dec_ha, decomp_file_img)

    img = Image.open(file_color)
    raw_data = PNG_to_RAW(img, raw_filename)
    print("ING_COL:")
    full_compress(raw_filename, temp_bwt_mtf, temp_rle, file_coded)
    full_decompress(temp_bwt_mtf, temp_rle, file_coded, temp_dec_ha, decomp_file_img)