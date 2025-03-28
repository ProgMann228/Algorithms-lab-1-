from BWT import bwt_transform, bwt_inverse
from MTF import MTF, iMTF
from collections import Counter
import os
import math
import matplotlib.pyplot as plt


def count_bytes(data):
    counts = Counter(data)
    total = len(data)
    return {byte: cnt / total for byte, cnt in counts.items()}


def calc_entropy(data):
    counts = count_bytes(data)
    entropy = 0.0
    for p in counts.values():
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy


def analyze_block_sizes(input_file, output_dir="entropy_analysis"):
    """Анализирует энтропию после BWT+MTF для разных размеров блоков"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(input_file, "rb") as f:
        data = f.read()

    # Тестируемые размеры блоков (степени двойки от 64 до 65536)
    block_sizes = [64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384]
    results = []

    for block_size in block_sizes:
        # Применяем BWT с текущим размером блока
        bwt_data, indices = bwt_transform(data, s=block_size)

        # Применяем MTF
        mtf_data = MTF(bwt_data)

        # Вычисляем энтропию
        entropy = calc_entropy(mtf_data)

        # Сохраняем результаты
        results.append((block_size, entropy))

        print(f"Размер блока: {block_size} байт | Энтропия: {entropy:.4f} бит/символ")



def compress(input_file: str, output_file: str, block_size=1024):
    """Сжимает файл с использованием BWT+MTF"""
    with open(input_file, "rb") as f:
        data = f.read()

    # Применяем BWT с указанным размером блока
    bwt_data, indices = bwt_transform(data, s=block_size)

    # Применяем MTF
    mtf_data = MTF(bwt_data)

    # Сохраняем сжатые данные (индексы + данные)
    with open(output_file, "wb") as f:
        f.write(len(indices).to_bytes(4, 'big'))
        [f.write(x.to_bytes(4, 'big')) for x in indices]
        f.write(mtf_data)

    original_size = os.path.getsize(input_file)

    print(f"Исходный размер: {original_size} байт")



def decompress(input_file: str, output_file: str):
    """Распаковывает файл, сжатый BWT+MTF"""
    with open(input_file, "rb") as f:
        num_indices = int.from_bytes(f.read(4), 'big')
        indices = [int.from_bytes(f.read(4), 'big') for _ in range(num_indices)]
        mtf_data = f.read()

    # Обратное MTF
    bwt_data = iMTF(mtf_data)

    # Обратное BWT
    original_data = bwt_inverse(bwt_data, indices)

    # Сохранение распакованных данных
    with open(output_file, "wb") as f:
        f.write(original_data)

    decompressed_size = os.path.getsize(output_file)
    entropy = calc_entropy(original_data)

    print(f"Размер после декомпрессии: {decompressed_size} байт")
    print(f"Энтропия декомпрессированных данных: {entropy:.4f} бит/символ")

"""
def main():
    # Пути к файлам
    file_enwik = "C:/Users/User/OneDrive/Документы/алгоритмы вуз/homework1/enwik9/enwik7.txt"
    compressed_file = "compressed.bin"
    decompressed_file = "decompressed.txt"

    print("Анализ зависимости энтропии от размера блоков BWT для enwik7:")
    analyze_block_sizes(file_enwik)

    # Тестируем сжатие с оптимальным размером блока (можно изменить)
    optimal_block_size = 1024  # Можно выбрать на основе анализа графика

    print("\nТестирование полного цикла сжатия/распаковки:")
    compress(file_enwik, compressed_file, block_size=optimal_block_size)
    decompress(compressed_file, decompressed_file)


if __name__ == "__main__":
    main()
"""