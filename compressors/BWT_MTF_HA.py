from BWT_MTF import compress as bwt_mtf_compress, decompress as bwt_mtf_decompress
from HA import encode_file as ha_encode, decode_file as ha_decode, Node, Haffman_tree,\
    build_min_heap, Counter, PNG_to_RAW
from PIL import Image

def full_compress(input_file,bwt_mtf_comp,comp_file):
    """Полное сжатие: BWT -> MTF -> Хаффман"""
    # Шаг 1: BWT + MTF
    print("Применяем BWT + MTF...")
    bwt_mtf_compress(input_file, bwt_mtf_comp, block_size=1024)

    # Шаг 2: Хаффман
    print("Применяем кодирование Хаффмана...")
    ha_encode(bwt_mtf_comp, comp_file)

    # Вывод информации о сжатии
    original_size = os.path.getsize(input_file)
    compressed_size = os.path.getsize(comp_file)
    print(f"\nИсходный размер: {original_size} байт")
    print(f"Сжатый размер: {compressed_size} байт")
    print(f"Коэффициент сжатия: {original_size / compressed_size:.2f}")


def full_decompress(bwt_mtf_comp,comp_file,dec_HA,dec_file):
    """Полная декомпрессия: Хаффман -> MTF -> BWT"""
    # Шаг 1: Декодирование Хаффмана
    print("\nДекодируем Хаффман...")
    with open(bwt_mtf_comp, "rb") as f:
        data = f.read()

    # Строим дерево Хаффмана
    freq = Counter(data)
    nodes = [Node(byte, count) for byte, count in freq.items()]
    huffman_tree = Haffman_tree(build_min_heap(nodes))

    # Декодируем
    ha_decode(comp_file, dec_HA, huffman_tree)

    # 2. Обратное BWT + MTF
    print("Обратное BWT + MTF...")
    bwt_mtf_decompress(dec_HA, dec_file)

    # Проверяем результаты
    decomp_size = os.path.getsize(dec_file)
    print(f"\nРазмер после распаковки: {decomp_size} байт")

if __name__ == "__main__":
    import os

    file_text = "D:/новая папка/PyCharm Community Edition 2024.2.3/sem2Laba1Alg/Приключения Незнайки.txt"
    file_enwik = "C:/Users/User/OneDrive/Документы/алгоритмы вуз/homework1/enwik9/enwik7.txt"
    file_exe = "C:/Users/User/OneDrive/Документы/алгоритмы вуз/homework1/aitstatic.exe"
    file_bw_img = "C:/Users/User/OneDrive/Документы/алгоритмы вуз/homework1/chernye-kruzhochki.jpg"
    file_gray_img = "C:/Users/User/OneDrive/Документы/алгоритмы вуз/homework1/Adams_The_Tetons_and_the_Snake_River.jpg"
    file_color = "C:/Users/User/OneDrive/Документы/алгоритмы вуз/homework1/AAA.jpg"
    raw_filename = "D:/новая папка/PyCharm Community Edition 2024.2.3/sem2Laba1Alg/image.raw"

    temp_coded="temp_code.bin"
    file_coded = "D:/новая папка/PyCharm Community Edition 2024.2.3/sem2Laba1Alg/HAcoded.bin"
    decomp_file_txt = "decompressed.txt"
    decomp_file_img = "decompressed.raw"
    temp_dec="temp_decode.bin"

    print("ENWIK:")
    full_compress(file_enwik, temp_coded, file_coded)
    full_decompress(temp_coded, file_coded, temp_dec, decomp_file_txt)

    print("TXT:")
    full_compress(file_text, temp_coded, file_coded)
    full_decompress(temp_coded, file_coded, temp_dec, decomp_file_txt)

    print("EXE:")
    full_compress(file_exe, temp_coded, file_coded)
    full_decompress(temp_coded, file_coded, temp_dec, decomp_file_txt)

    img = Image.open(file_bw_img)
    raw_data = PNG_to_RAW(img, raw_filename)
    print("ING_BW:")
    full_compress(raw_filename, temp_coded, file_coded)
    full_decompress(temp_coded, file_coded, temp_dec, decomp_file_img)

    img = Image.open(file_gray_img)
    raw_data = PNG_to_RAW(img, raw_filename)
    print("IMG_GREY:")
    full_compress(raw_filename, temp_coded, file_coded)
    full_decompress(temp_coded, file_coded, temp_dec, decomp_file_img)

    img = Image.open(file_color)
    raw_data = PNG_to_RAW(img, raw_filename)
    print("ING_COL:")
    full_compress(raw_filename, temp_coded, file_coded)
    full_decompress(temp_coded, file_coded, temp_dec, decomp_file_img)


