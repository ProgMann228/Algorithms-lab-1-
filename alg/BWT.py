def bwt_transform(d: bytes, s=1024):
    t, i = bytearray(), []
    for j in range(0, len(d), s):
        idx, enc = transform_chunk(d[j:j + s])
        t.extend(enc), i.append(idx)
    return bytes(t), i

def transform_chunk(c: bytes):
    r = sorted(c[i:] + c[:i] for i in range(len(c)))
    return r.index(c), bytes(x[-1] for x in r)

def bwt_inverse(t: bytes, i: list[int], s=1024):
    r, p, x = bytearray(), 0, 0
    while p < len(t):
        r.extend(reverse_transform_chunk(i[x], t[p:p + s]))
        p += s; x += 1
    return bytes(r)

def reverse_transform_chunk(i: int, e: bytes):
    t = sorted((c, n) for n, c in enumerate(e))
    r, row = bytearray(), i
    for _ in range(len(e)):
        c, row = t[row]
        r.append(c)
    return bytes(r)

def process_file(f1, f2, f3):
    with open(f1, "rb") as f: d = f.read()
    t, i = bwt_transform(d)
    with open(f2, "wb") as f:
        f.write(len(i).to_bytes(4, 'big'))
        [f.write(x.to_bytes(4, 'big')) for x in i]
        f.write(t)
    with open(f2, "rb") as f:
        n = int.from_bytes(f.read(4), 'big')
        i = [int.from_bytes(f.read(4), 'big') for _ in range(n)]
        t = f.read()
    with open(f3, "wb") as f: f.write(bwt_inverse(t, i))
    print(f"Done: {f1} -> {f2}, {f3}")

"""
# Задание путей к файлам
file1="D:/новая папка/PyCharm Community Edition 2024.2.3/sem2Laba1Alg/Приключения Незнайки.txt"
file2= "D:/новая папка/PyCharm Community Edition 2024.2.3/sem2Laba1Alg/HAcoded.bin"
file3 = "D:/новая папка/PyCharm Community Edition 2024.2.3/sem2Laba1Alg/HAdecoded.txt"

# Обработка файла
process_file(file1, file2, file3)

"""

