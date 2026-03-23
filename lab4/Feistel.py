import os
import sys

_THIS_DIR = os.path.dirname(__file__)
_LAB1_DIR = os.path.abspath(os.path.join(_THIS_DIR, "..", "lab1"))
_LAB2_DIR = os.path.abspath(os.path.join(_THIS_DIR, "..", "lab2"))
_LAB3_DIR = os.path.abspath(os.path.join(_THIS_DIR, "..", "lab3"))
if _LAB1_DIR not in sys.path:
    sys.path.append(_LAB1_DIR)

if _LAB2_DIR not in sys.path:
    sys.path.append(_LAB2_DIR)

if _LAB3_DIR not in sys.path:
    sys.path.append(_LAB3_DIR)

from LinearCongruentialGenerator import block2num, dec2bin, bin2dec, num2block, C_CT_LSG_NEXT  # type: ignore
from c_block import text2array, array2text, add_txt, sub_txt # type: ignore
from TritimiusCipher import TrithemiusCipher # type: ignore

def subblocks_xor(BLOCKA_IN, BLOCKB_IN):
    """
    Операция побитного XOR.
 
    :param BLOCKA_IN:       левая строка
    :param BLOCKB_IN:       правая строка
    :return:                результат XOR над строками
    """
    decA = block2num(BLOCKA_IN)
    decB = block2num(BLOCKB_IN)
    binA = dec2bin(decA)
    binB = dec2bin(decB)
    binO = [( binA[i] + binB[i]) % 2 for i in range(len(binA))]
    decO = bin2dec(binO)
    out = num2block(decO)
    return out
 
 
def block_xor(BLOCKA_IN, BLOCKB_IN):
    nb = len(BLOCKA_IN) // 4
    out = ""
    for i in range(nb):
        tmpA = BLOCKA_IN[i*4 : i*4 + 4]
        tmpB = BLOCKB_IN[i*4 : i*4 + 4]
        out = out + subblocks_xor(tmpA, tmpB)
    return out
 
 
# inA = "АГАТ"
# inB = "ТАГА"
 
# inA1 = "КОЛЕНЬКА"
# inB1 = "МТВ_ТЛЕН"

# inA2 = "ТОРТ_ХОЧЕТ_ГОРКУ"  
# inB2 = "МТВ_ВСЕ_ЕЩЕ_ТЛЕН"
 
# print("block_xor(inA, inB):", block_xor(inA, inB))
# print("block_xor(inA1, inB1):", block_xor(inA1, inB1))
# print("block_xor(inA2, inB2):", block_xor(inA2, inB2))
# out = block_xor(inA2, inB2)
# print("block_xor(out, inB2):", block_xor(out, inB2))

def produce_round_keys(KEY_IN, num_in, RNG_SET):
    """
    Обёртка для применения ГСК в блочном шифровании.
 
    :param KEY_IN:       основной ключ (16 символов)
    :param num_in:       число генерируемых значений (блоков по 16 символов)
    :param RNG_SET:      набор констант для ГСК, оставьте None
    :return:             список из num_in блоков по 16 символов
    """
    if RNG_SET == None:
        set1 = [None] * 3
        set1[0] = [252564, 9109, 961193]
        set1[1] = [252564, 9109, 961193]
        set1[2] = [723482, 8677, 983609]
        SET_0 = set1

        # set2
        set2 = [None] * 3
        set2[0] = [51190, 7927, 990711]
        set2[1] = [51190, 7927, 990711]
        set2[2] = [549234, 6949, 939683]
        SET_1 = set2

        # set3
        set3 = [None] * 3
        set3[0] = [227796, 5107, 981875]
        set3[1] = [227796, 5107, 981875]
        set3[2] = [167490, 9871, 809137]
        SET_2 = set3

        # set4
        set4 = [None] * 3
        set4[0] = [357630, 8971, 948209]
        set4[1] = [357630, 8971, 948209]
        set4[2] = [73335, 6779, 1014784]
        SET_3 = set4

        SET = [SET_0, SET_1, SET_2, SET_3]
        RNG_SET = SET
    # Первый шаг: генерация начального out и intern с направлением "up"
    out_0, intern = C_CT_LSG_NEXT("up", -1, KEY_IN, RNG_SET)
    out = [out_0]
 
    if num_in > 1:
        for i in range(1, num_in):          # i в 1..num_in-1
            out_i, intern = C_CT_LSG_NEXT("down", intern, -1, RNG_SET)
            out.append(out_i)
 
    return out

# key = "ПОЛИМАТ_ТЕХНОБОГ"
# strlen = 16
# print(produce_round_keys(key, 6, None))

def frw_P_scitala(BLOCK_IN):
    """
    Шифр перестановки "Скитала".
 
    :param BLOCK_IN:       открытый текст
    :return:             шифротекст
    """
    T = text2array(BLOCK_IN)
    q = len(BLOCK_IN) // 2
    f = len(BLOCK_IN) % 2
    tmpA = BLOCK_IN[0 : q + f]
    tmpB = BLOCK_IN[q + f : q + f + q]
    out = ""
    for i in range(q + 1):  # i в 0..q
        if i % 2 == 0:
            out += tmpA[i : i + 1]
            out += tmpB[i : i + 1]
        else:
            out += tmpB[i : i + 1]
            out += tmpA[i : i + 1]
    if f == 1:
        out += tmpA[q + f : q + f + 1]
    return out
 
 
def inv_P_scitala(BLOCK_IN):
    """
    Шифр перестановки "Скитала".
 
    :param BLOCK_IN:       шифротекст
    :return:             открытый текст
    """
    T = text2array(BLOCK_IN)
    q = len(BLOCK_IN) // 2
    f = len(BLOCK_IN) % 2
    tmpA = ""
    tmpB = ""
    out = ""
    for i in range(q):  # i в 0..q-1
        if i % 2 == 0:
            tmpA += BLOCK_IN[2 * i     : 2 * i + 1]
            tmpB += BLOCK_IN[2 * i + 1 : 2 * i + 2]
        else:
            tmpB += BLOCK_IN[2 * i     : 2 * i + 1]
            tmpA += BLOCK_IN[2 * i + 1 : 2 * i + 2]
    if f == 1:
        tmpA += BLOCK_IN[2 * q : 2 * q + 1]
    out = tmpA + tmpB
    return out

# inp = "АЭРОСМИТ"
# o = frw_P_scitala(inp)
# print(o)
# print(inv_P_scitala(o))
# tests_frw = [
#         ("ДЖИГУРДА",  "ДУРЖИДАГ"),
#         ("ДЖИГУРДАЯ", "ДРДЖИАЯГУ"),
#         ("АЭРОСМИТ",  "АСМЭРИТО"),
#         ("БАЭРОСМИТ", "БСМАЭИТРО"),
#     ]
# tests_inv = [
#         ("ДУРЖИДАГ",  "ДЖИГУРДА"),
#         ("ДРДЖИАЯГУ", "ДЖИГУРДАЯ"),
#         ("АСМЭРИТО",  "АЭРОСМИТ"),
#         ("БСМАЭИТРО", "БАЭРОСМИТ"),
#     ]
 
# print("=== frw_P_scitala ===")
# for inp, expected in tests_frw:
#     result = frw_P_scitala(inp)
#     status = "OK" if result == expected else f"FAIL (got {result})"
#     print(f"  frw_P_scitala({inp!r}) = {result!r}  [{status}]")
 
# print("=== inv_P_scitala ===")
# for inp, expected in tests_inv:
#     result = inv_P_scitala(inp)
#     status = "OK" if result == expected else f"FAIL (got {result})"
#     print(f"  inv_P_scitala({inp!r}) = {result!r}  [{status}]")
 
def frw_routine_Feistel(BLOCK_IN, KEY_IN):
    """
    Одиночная петля Фейстеля.
 
    :param BLOCK_IN:       открытый текст
    :param KEY_IN           ключ
    :return:             шифротекст
    """
    left = BLOCK_IN[0:4]
    right = BLOCK_IN[4:8]
    tmp = TrithemiusCipher.s_block_encrypt(right, KEY_IN)
    left  = add_txt(tmp, left)
    out   = right + left
    return out

def inv_routine_Feistel(BLOCK_IN, KEY_IN):
    """
    Одиночная петля Фейстеля.
 
    :param BLOCK_IN:       шифротекст
    :param KEY_IN           ключ
    :return:             открытый текст
    """
    l     = len(BLOCK_IN)
    left  = BLOCK_IN[0 : l // 2]
    right = BLOCK_IN[l // 2 : l // 2 + l // 2]
    tmp = TrithemiusCipher.s_block_encrypt(left, KEY_IN)
    right = sub_txt(right, tmp)
    out   = right + left
    return out


# key = "ЗОЛОТУХА_ПИКЕТКА"
# block = "АААААААА"
# f = frw_routine_Feistel(block, key)
# print(f)
# print(inv_routine_Feistel(f, key))
# tests = [
#     ("ГОР_СВЕТ", "СВЕТДКЩВ",  "СВЕТНДОЬ"),
#     ("ЕГОР_КОТ", "_КОТООЙ_",  "_КОТМТЯ_"),
#     ("АААААААА", "АААЕОЛИ",   "ААААПРШ"),
#     ("ААААААА_", "ААА_ЕЮЫШ",  "ААА_КШНЦ"),
# ]
 
# inv_tests = [
#     ("СВЕТДКЩВ",  "ГОР_СВЕТ"),
#     ("_КОТООЙ_",  "ЕГОР_КОТ"),
#     ("ААААЕОЛИ",   "АААААААА"),
#     ("ААА_ЕЮЫШ",  "ААААААА_"),
# ]
 
# # ---------------------------------------------------------------------------
# # Прямые тесты
# # ---------------------------------------------------------------------------
# print("=== frw_routine_Feistel ===")
# for inp, exp_t, _ in tests:
#     res = frw_routine_Feistel(inp, key)
#     status = "OK" if res == exp_t else f"FAIL (got {res!r})"
#     print(f"  frw(Trith, {inp!r}) = {exp_t!r}  [{status}]")
 
 
# # ---------------------------------------------------------------------------
# # Обратные тесты
# # ---------------------------------------------------------------------------
# print("\n=== inv_routine_Feistel ===")
# for inp, expected, in inv_tests:
#     res = inv_routine_Feistel(inp, key)
#     status = "OK" if res == expected else f"FAIL (got {res!r})"
#     print(f"{inp!r}) = {expected!r}  [{status}]")

def block2bin(BLOCK_IN):
    """
    Перевод текста в двоичный код.
 
    :param BLOCK_IN:       текст
    :return:             массив бит
    """
    indexes = text2array(BLOCK_IN)
    bit = [None] * len(BLOCK_IN)
    for i in range(len(BLOCK_IN)):
        bit[i] = dec2bin(indexes[i])
    b = [item for row in bit for item in row]
    return b

def bin2block(BIN_IN):
    """
    Перевод двоичного кода в текст.
 
    :param BLOCK_IN:       массив бит
    :return:             текст
    """
    b_new = [BIN_IN[i:i+20] for i in range(0, len(BIN_IN), 20)]
    nums = [None] * len(b_new)
    for i in range(len(b_new)):
        nums[i] = bin2dec(b_new[i])
    txt = array2text(nums)
    return txt

def bit_swap(BLOCK_IN):
    """
    Меняет четные биты на нечетные
 
    :param BLOCK_IN:       массив бит
    :return:             массив бит
    """
    b = block2bin(BLOCK_IN[0:4])
    for i in range(40):
        t = b[2 * i]
        b[2 * i] = b[2 * i + 1]
        b[2 * i + 1] = t
    txt = bin2block(b)
    return txt + BLOCK_IN[4:8]

def bit_shift(BLOCK_IN):
    """
    Сдвиг битов.
 
    :param BLOCK_IN:       массив бит
    :return:             текст
    """
    b = block2bin(BLOCK_IN[0:4])
    t = b[19]
    for i in range(19, 1, -1):
        b[i] = b[i - 1]
    b[0] = t
    txt = bin2block(b)
    return txt + BLOCK_IN[4:8]

def bit_shift_r(BLOCK_IN):
    """
    Сдвиг битов в другую сторону
 
    :param BLOCK_IN:       массив бит
    :return:             текст
    """
    b = block2bin(BLOCK_IN[0:4])
    t = b[0]
    for i in range(19):
        b[i] = b[i + 1]
    b[19] = t
    txt = bin2block(b)
    return txt + BLOCK_IN[4:8]

# X = "ПРОВОРПВ"
# print(bit_swap(X))
# sh = bit_shift(X)
# print(sh)
# print(bit_shift_r(sh))

def frw_inner_Feistel(BLOCK_IN, KEY_IN, r_in):
    """
    Петля фейстеля
 
    :param BLOCK_IN:       открытый текст
    :param KEY_IN           ключ
    :param r_in             число раундов
    :return:             шифротекст
    """
    tmp = bit_swap(frw_P_scitala(BLOCK_IN))
    for i in range(r_in - 1):         
        tmp = frw_routine_Feistel(tmp, KEY_IN)
        tmp = bit_shift(tmp)
    out = frw_P_scitala(bit_swap(tmp))
    return out
 
 
def inv_inner_Feistel(BLOCK_IN, KEY_IN, r_in):
    """
    Петля фейстеля
 
    :param BLOCK_IN:       шифротекст
    :param KEY_IN           ключ
    :param r_in             число раундов
    :return:             открытый текст
    """
    tmp = bit_swap(inv_P_scitala(BLOCK_IN))
    for i in range(r_in - 1, 0, -1):   
        tmp = bit_shift_r(tmp)
        tmp = inv_routine_Feistel(tmp, KEY_IN)
    out = inv_P_scitala(bit_swap(tmp))
    return out

# key = "ЗОЛОТУХА_ПИКЕТКА"
# block = "ПЕТУШАРА"
# out = frw_inner_Feistel(block, key, 4)
# print(out)
# print(inv_inner_Feistel(out, key, 4))
# inputs = [("ГОР_СВЕТ", "in1"), ("ЕГОР_КОТ", "in2")]
 
# cases = [
#     ("Trithemus", 1),
#     ("Trithemus", 2),
#     ]
 
# print("=== frw_inner_Feistel + круговая проверка inv(frw(x)) == x ===\n")
# for s_name, r in cases:
#     print(f"  [{s_name}, r={r}]")
#     for inp, label in inputs:
#         frw_out = frw_inner_Feistel(inp, key, r)
#         inv_out = inv_inner_Feistel(frw_out, key, r)
#         status = "OK" if inv_out == inp else f"FAIL (inv={inv_out!r})"
#         print(f"    frw({label}={inp!r}) = {frw_out!r}  | inv → {inv_out!r}  [{status}]")
#     print()

def swap_blocks(BLOCK_IN):
    return BLOCK_IN[8:16] + BLOCK_IN[0:8]

# def block_xor(BLOCK_IN1, BLOCK_IN2):
#     m = min(len(BLOCK_IN1), len(BLOCK_IN2))
#     b1 = block2bin(BLOCK_IN1)
#     b2 = block2bin(BLOCK_IN2)
#     b3 = [None] * (m * 20)
#     for i in range(m * 20):
#         b3[i] = 1 if b1[i] == b2[i] else 0
#     txt = bin2block(b3)
#     return txt

def round_Feistel(BLOCK_IN, KEY_IN):
    """
    Раунд петли Фейстеля
 
    :param BLOCK_IN:       подготовленный к шифрованию текст
    :param KEY_IN           ключ
    :return:             почти шифротекст
    """
    left = BLOCK_IN[0:8]
    right = BLOCK_IN[8:16]
    tmp = frw_inner_Feistel(right, KEY_IN, 3)
    left = block_xor(tmp, left)
    return right + left

# key  = "МТВ_ВСЕ_ЕЩЕ_ТЛЕН"
# in1  = "КОРЫСТЬ_СЛОНА_ЭХ"
# in2  = "НУЖНО_БОЛЬШЕ_ПЫЩ"

# print("=== round_Feistel (Trithemus) ===")
# cases_t = [
#     (in1, "СЛОНА_ЭХ_ЦПТЩИЙОЮ"),
#     (in2, "ЛЫШЕ_ПЫЩЗГФИЮЩЖЕ"),
# ]
# for inp, expected in cases_t:
#     res = round_Feistel(inp, key)
#     status = "OK" if res == expected else f"FAIL (got {res!r})"
#     print(f"  round_Feistel({inp!r}) = {expected!r}  [{status}]")
 
# print("\n=== swap_blocks (Trithemus, round 1) ===")
# out1t = round_Feistel(in1, key)
# out2t = round_Feistel(in2, key)
# cases_swap_t = [
#     (out1t, "_ЦПТЩИЙОЮСЛОНА_ЭХ"),
#     (out2t, "ЗФИЮЩЖЕЛЬШЕ_ПЫЩ"),
# ]
# for inp, expected in cases_swap_t:
#     res = swap_blocks(inp)
#     status = "OK" if res == expected else f"FAIL (got {res!r})"
#     print(f"  swap_blocks({inp!r}) = {expected!r}  [{status}]")
 
# print("\n=== round_Feistel (Trithemus, round 2 on swapped) ===")
# tmp1t = swap_blocks(out1t)
# tmp2t = swap_blocks(out2t)
# cases_t2 = [
#     (tmp1t, "СЛОНА_ЭХКОРЫСТЬ_"),
#     (tmp2t, "ЛЫШЕ_ПЫЩНУЖНО_БО"),
# ]
# for inp, expected in cases_t2:
#     res = round_Feistel(inp, key)
#     status = "OK" if res == expected else f"FAIL (got {res!r})"
#     print(f"  round_Feistel({inp!r}) = {expected!r}  [{status}]")
 
# print("\n=== swap_blocks (Trithemus, round 2) → исходные блоки ===")
# ltmp1t = round_Feistel(tmp1t, key)
# ltmp2t = round_Feistel(tmp2t, key)
# cases_swap_t2 = [
#     (ltmp1t, in1),
#     (ltmp2t, in2),
# ]
# for inp, expected in cases_swap_t2:
#     res = swap_blocks(inp)
#     status = "OK" if res == expected else f"FAIL (got {res!r})"
#     print(f"  swap_blocks({inp!r}) = {expected!r}  [{status}]")

def frw_Feistel(BLOCK_IN, KEYS_IN, r_in):
    """
    Многораундовое шифрование Фейстеля
 
    :param BLOCK_IN:       открытый текст
    :param KEY_IN           ключ
    :param r_in             число раундов не меньше 2
    :return:             шифротекст
    """
    key_set = KEYS_IN
    block = block_xor(BLOCK_IN, key_set[0])
    for i in range(1, r_in+1, 1):
        block = round_Feistel(block, key_set[i])
    return block_xor(block, key_set[r_in + 1])

def inv_Feistel(BLOCK_IN, KEYS_IN, r_in):
    """
    Многораундовое шифрование Фейстеля
 
    :param BLOCK_IN:       шифротекст
    :param KEY_IN           ключ
    :param r_in             число раундов не меньше 2
    :return:             открытый текст
    """
    key_set = KEYS_IN
    block = block_xor(BLOCK_IN, key_set[r_in + 1])
    block = swap_blocks(block)
    for i in range(r_in, 0, -1):
        block = round_Feistel(block, key_set[i])
    block = swap_blocks(block)
    return block_xor(block, key_set[0])  

# key  = "МТВ_ВСЕ_ЕЩЕ_ТЛЕН"
# in1  = "КОРЫСТЬ_СЛОНА_ЭХ"
# in2  = "НУЖНО_БОЛЬШЕ_ПЫЩ"

# keys = produce_round_keys(key, 6, None)

# out1 = frw_Feistel(in1, keys, 1)
# lout1 = inv_Feistel(out1, keys, 1)
# out2 = frw_Feistel(in2, keys, 4)
# lout2 = inv_Feistel(out2, keys, 4)
# print(keys)
# print("=" * 20)
# print(out1)
# print(lout1)
# print(out2)
# print(lout2)