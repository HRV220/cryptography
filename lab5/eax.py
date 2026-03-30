import os
import sys

_THIS_DIR = os.path.dirname(__file__)
_LAB1_DIR = os.path.abspath(os.path.join(_THIS_DIR, "..", "lab1"))
_LAB2_DIR = os.path.abspath(os.path.join(_THIS_DIR, "..", "lab2"))
_LAB3_DIR = os.path.abspath(os.path.join(_THIS_DIR, "..", "lab3"))
_LAB4_DIR = os.path.abspath(os.path.join(_THIS_DIR, "..", "lab4"))
if _LAB1_DIR not in sys.path:
    sys.path.append(_LAB1_DIR)

if _LAB2_DIR not in sys.path:
    sys.path.append(_LAB2_DIR)

if _LAB3_DIR not in sys.path:
    sys.path.append(_LAB3_DIR)

if _LAB4_DIR not in sys.path:
    sys.path.append(_LAB4_DIR)

from c_block import MerDam_hash   # type: ignore
from LinearCongruentialGenerator import block2num, dec2bin, bin2dec, num2block # type: ignore
from Alphabet import TelegraphAlphabet
t = TelegraphAlphabet()

def num2sym(num):
    """
    Преобразует число в букву алфавита по её индексу
    
    Args:
        num: число
    
    Returns:
        char: буква алфавита
    """
    return str(t.get_char_by_value(num))

def sym2num(sym):
    """
    Преобразует букву алфавита в число
    
    Args:
        sym: буква
    
    Returns:
        int: индекс
    """
    return t.get_value_by_char(sym)

def KDF(MAT_IN, SALT_IN, CON_IN, SIZE_IN, iter_in):
    """
    Генерирует любое количество ключей
    
    Args:
        MAT_IN: строка телеграфного алфавита
        SALT_IN: строка телеграфного алфавита
        CON_IN: массив строк телеграфного алфавита
        SIZE_IN: массив int, размеры ключей
        iter_in: число ключей int
    
    Returns:
        list[string]: список ключей
    """
    out = []
    tmp = MAT_IN + SALT_IN
    for i in range(iter_in+1):
        ext = MerDam_hash(tmp)
        tmp = ext + tmp
    PRK = tmp
    for i in range(len(SIZE_IN)):
        q = (SIZE_IN[i] - (SIZE_IN[i] % 64)) // 64
        rem = i
        res = ""
        while rem > 0:
            h = rem % 32
            res += str(num2sym(h))
            rem = (rem - h) / 32
        if q > 0:
            hash = PRK
            for j in range(q + 1):
                tmp = hash + CON_IN[i] + PRK
                hash = MerDam_hash(tmp)
                res = hash + res
        else:
            tmp = PRK + CON_IN[i] + PRK
            res = MerDam_hash(tmp)
        out.append(res[0: SIZE_IN[i]])
    return out

# PASS1 = "ЧЕЧЕТКА"
# PASS2 = "АПРОЛ"
# SALT1 = "СЕАНС"
# SALT2 = "АТЛЕТ"
# CONTEXT = ["СЕАНСОВЫЙ_КЛЮЧ", "КЛЮЧ_РАСПРЕДЕЛЕНИЯ_КЛЮЧЕЙ"]
# SIZE = [32, 16]

# print(KDF(PASS1, SALT1, CONTEXT, SIZE, 2))
# RR = KDF(PASS1, SALT2, ["МАСТЕР_КЛЮЧ"], [120], 2)
# print(len(RR[0]))

def sym2bin(s_in: str) -> int:
    """
    Преобразует строковый символ '0' или '1' в целое число.
    
    Args:
        s_in: строка, содержащая символ '0' или '1'
    
    Returns:
        int: 0 или 1
    """
    return int(s_in[0])

# print(sym2bin("1"))
# print(sym2bin("2"))

def isSym(s_in: str) -> int:
    """
    Проверяет, является ли символ допустимым (буквой русского алфавита или '_').
    
    Args:
        s_in: строка, содержащая один символ
    
    Returns:
        int: 1 если символ найден, -1 если не найден
    """
    C = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЫЬЭЮЯ_"
    
    # Проверяем, есть ли символ в строке C
    if s_in in C:
        return 1
    else:
        #print(s_in)
        return -1
    
def msglen(MSG_IN):
    """
    Вспомогательная функция, нигде больше не используется
    
    Args:
        MSG_IN: строка телеграфного алфавита с возможными 0 или 1 на конце
    
    Returns:
        int, int: количество букв, количество цифр
    """
    l = 0
    ll = len(MSG_IN)
    i = 0
    while isSym(MSG_IN[i]) == 1:
        l = l + 1
        i = i + 1
        if i == ll:
            break
    a = ll - l
    return l, a


def msg2bin(MSG_IN):
    """
    Преобразует строку в массив бит. Каждая буква заменяется 5 битами, числа остаются как есть
    
    Args:
        MSG_IN: строка из букв с возможными 0 или 1 на конце
    
    Returns:
        list[bit]: список 0 и 1
    """
    M, l = msglen(MSG_IN)
    i = 0
    tmp = [None] * M * 5 + [None] * l
    while isSym(MSG_IN[i]) == 1:
        p = MSG_IN[i]
        c = sym2num(p)
        for j in range(5):
            tmp[i * 5 + 4 - j] = c % 2
            c = c // 2
        if i == M - 1:
            break
        else:
            i = i + 1
    if l != 0:
        for k in range(i + 1, M + l, 1):
            p = MSG_IN[k]
            tmp[4 * i + k + 4] = sym2bin(p) 
    return tmp

# TEST = "ГНОЛЛЫ_ПИЛИЛИ_ПЫЛЕСОС_ЛОСОСЕМ0011"
# q = msg2bin(TEST)
# print(q)
# print(len(q))

def bin2msg(BIN_IN):
    """
    Преобразует массив битов в строку из букв и возможно из 0 и 1
    Если 0 и 1 в конце РОВНО 5 то заменятся БУКВОЙ, это правильно
    Args:
        BIN_IN: массив битов
    
    Returns:
        string: строка телеграфоного алфавита с возможными 0 и 1 в конце
    """
    B = len(BIN_IN)
    b = B // 5
    q = B % 5
    out = ""
    for i in range(b):
        t = 0
        for j in range(5):
            t = 2 * t + BIN_IN[i * 5 + j]
        out += str(num2sym(t))
    if q > 0:
        for k in range(1, q + 1, 1):
            out = out + str(BIN_IN[b * 5 + k - 1])
    return out

# print(bin2msg(q))

# далее работаем со строками из файла
file_path = r'C:\Users\Welldoneny\Desktop\cryptography\lab5\inp.txt'
with open(file_path, 'r', encoding='utf-8') as file:
    INPUT_ARRAY = file.readlines()

# # Удаляем символы \n из каждой строки
INPUT_ARRAY = [line.rstrip('\n') for line in INPUT_ARRAY]
# q = msg2bin(INPUT_ARRAY[3])
# print(bin2msg(q))

ASSOCDATA_ARRAY = [
    ["ВА", "АЛИСА__А", "БОБ____А", "КОТОПОЕЗД"],
    ["ВБ", "АЛИСА_АЖ", "БОБ___ОЧ", "ЕГИПТЯНИН"],
    ["В_", "АЛИСА_ЯЗ", "БОБ___ЬЬ", "ЩЕГОЛЯНИЕ"],
    ["ВБ", "БОБ___ЬЬ", "АЛИСА_ЯЗ", "ЭКЛАМПСИЯ"],
    ["ВБ", "БОБ___ЬЬ", "АЛИСА_ЯЗ", "ЕГИПТЯНИН"],
    ["ВБ", "АЛИСА_ЯЗ", "БОБ___ЬЬ", "ЕГИПТЯНИН"]
]

def check_padding(BINMSG_IN):
    """
    Проверяет подложку в конце сообщения
    
    Args:
        BINMSG_IN: массив битов
    
    Returns:
        f: есть ли подложка
        numblocks: количество блоков
        padlength: размер подложки
    """
    numblocks = 0
    padlength = 0
    BINS = BINMSG_IN
    M = len(BINMSG_IN)
    blocks = M // 80
    remainder = M % 80
    if remainder == 0:
        tb = BINS[M - 20 : M]
        ender = tb[17 : 20]
        if ender == [0, 0, 1]:
            NB = tb[7 : 17]
            PL = tb[0 : 7]
            for i in range(7):
                padlength = 2 * padlength + PL[i]
            for i in range(10):
                numblocks = 2 * numblocks + NB[i]
            if numblocks == blocks and padlength >= 23 and padlength < 103:
                tb = BINS[M - padlength : M - 20]
                starter = tb[0]
                if starter == 1:
                    f = 1
                    for j in range(1, padlength - 20, 1):
                        tmp = tb[j]
                        if tmp == 1:
                            f = 0
                            break;
                        break;
            else:
                f = 0
        else:
            f = 0
    else:
        f= 0
    return [f, [numblocks, padlength]]

def produce_padding(rem_in, blocks_in):
    """
    Создает подложку
    
    Args:
        rem_in: число не достающих битов
        blocks_in: количество блоков
    
    Returns:
        list[bit]: подложка
    """
    if rem_in == 0:
        b = blocks_in + 1
        r = 80
    elif rem_in <= 57:
        r = 80 - rem_in
        b = blocks_in + 1
    else:
        b = blocks_in + 2
        r = 160 - rem_in
    pad = [None] * r
    pad[0] = 1
    for i in range(1, r-20, 1):
        pad[i] = 0
    rt = r
    for i in range(6, -1, -1):
        pad[r - 20 + i] = rt % 2
        rt = rt // 2
    for i in range(9, -1, -1):
        pad[r - 13 + i] = b % 2
        b = b // 2
    pad[r - 3] = 0
    pad[r - 2] = 0
    pad[r - 1] = 1
    return pad

def pad_message(MSG_IN):
    """
    Добавляет подложку в сообщение
    
    Args:
        MSG_IN: сообщение без подложки
    
    Returns:
        string: сообщение с подложкой
    """
    pad = ""
    BINS = msg2bin(MSG_IN)
    M = len(BINS)
    blocks = M // 80
    remainder = M % 80
    if remainder == 0:
        f = check_padding(BINS)[0]
    else:
        f = 1
    if f == 1:
        pad = produce_padding(remainder, blocks)
        for j in range(len(pad)):
            BINS.append(pad[j])
    return bin2msg(BINS)

def unpad_message(MSG_IN):
    """
    Убирает подложку
    
    Args:
        MSG_IN: сообщение с подложкой
    
    Returns:
        string: сообщение без подложки
    """
    BINS = msg2bin(MSG_IN)
    M = len(BINS)
    T = check_padding(BINS)
    if T[0] == 1:
        pl = T[1][1]
        tmp = BINS[0 : M - pl]
        return bin2msg(tmp)
    else:
        return MSG_IN
    
# IN = INPUT_ARRAY[0]
# print(len(IN))
# print(len(msg2bin(IN)))
# INTER = pad_message(IN)
# print(len(INTER))
# print(len(msg2bin(INTER)))
# OUT = unpad_message(INTER)
# print(len(OUT))
# print(len(msg2bin(OUT)))

# IN = INPUT_ARRAY[3]
# print(len(IN))
# print(len(msg2bin(IN)))
# tmp = check_padding(msg2bin(IN))
# print(tmp[0])
# print(tmp[1])
# INTER = pad_message(IN)
# print(len(INTER))
# print(len(msg2bin(INTER)))
# tmp = check_padding(msg2bin(INTER))
# print(tmp[0])
# print(tmp[1])
# OUT = unpad_message(INTER)
# print(len(OUT))
# print(len(msg2bin(OUT)))
# print(msg2bin(OUT) == msg2bin(IN))

def prepare_packet(DATA_IN, IV_in, MSG_IN):
    """
    Подготавливает пакет с сообщением перед отправкой
    
    Args:
        DATA_IN: массив из: тип сообщения, отправитель, получатель, сессия
        IV_in: инициализируеще значение
        MSG_IN: текст сообщения
    
    Returns:
        list[]: данные, инициализируеще значение, сообщение с подложкой, мак
    """
    data = DATA_IN
    iv = "_" * 9 + IV_in
    msg = pad_message(MSG_IN)
    L = len(msg2bin(msg))
    a = ""
    for i in range(5):
        a = num2sym(L % 32) + a
        L = L // 32
    data.append(a)
    mac = ""
    return [data, iv, msg, mac]

def transmit(PACKET_IN):
    """
    Имитация отправки сообщения
    
    Args:
        PACKET_IN: пакетик с сообщением
    
    Returns:
        STREAM: поток битов
    """
    data = PACKET_IN[0]
    iv = PACKET_IN[1]
    msg = PACKET_IN[2]
    mac = PACKET_IN[3]
    t = data[0] + data[1] + data[2] + data[3] + data[4]
    return msg2bin(t + iv + msg + mac)

def recieve(STREAM_IN):
    """
    Имитация приема сообщения
    
    Args:
        STREAM_IN: поток битов
    
    Returns:
        PACKET: сообщение со всей служебной информацией
    """
    p = bin2msg(STREAM_IN)
    M = len(p)
    type = p[0:2]
    sender = p[2:10]
    reciever = p[10:18]
    session = p[18: 27]
    length = p[27: 32]
    iv = p[32:47]
    L = 0
    for i in range(5):
        t = length[i]
        l = sym2num(t)
        L = 32 * L + l
    L = L // 5
    message = p[47:47+L]
    mac = p[47+L:M]
    return [[type, sender, reciever, session, length], iv, message, mac]

# XTST = prepare_packet(ASSOCDATA_ARRAY[1], "КОЛЕСО", INPUT_ARRAY[1])
# YTST = recieve(transmit(XTST))

# print(XTST[2] == YTST[2])
# print(XTST[1])
# print(XTST[0])
# print(XTST[3])
# print(YTST[0])
# print(YTST[1])
# print(YTST[3])
# print(YTST[2])
# print(sym2num("П") + 32 * sym2num("Б") + 32 ** 2 * sym2num("О"))

def textor(A_IN, B_IN):
    out = ""
    C = [None] * 80
    for i in range(4):
        a = A_IN[i*4:i*4+4]
        b = B_IN[i*4:i*4+4]
        A = dec2bin(block2num(a))
        B = dec2bin(block2num(b))
        for j in range(20):
            C[j] = (A[j] + B[j]) % 2
        c = bin2dec(C)
        out = out + num2block(c)
    return out

# A1 = "ГОЛОВКА_КРУЖИТСЯ"
# A2 = "МЫШКА_БЫЛА_ЛИХОЙ"
# B1 = "СИНЕВАТАЯ_БОРОДА"
# B2 = "ЗЕЛЕНЫЙ_КОТОЗМИЙ"
# C1 = textor(A1, A2)
# C2 = textor(A1, B2)
# print(C1)
# print(C2)
# print(textor(C1, A2))
# print(textor(C1, A1))
# print(textor(C2, A1))
# print(textor(C2, A2))

