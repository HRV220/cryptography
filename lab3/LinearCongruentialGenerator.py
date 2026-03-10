import os
import sys

# Корректный импорт модулей ЛР1, ЛР2
_THIS_DIR = os.path.dirname(__file__)
_LAB1_DIR = os.path.abspath(os.path.join(_THIS_DIR, "..", "lab1"))
_LAB2_DIR = os.path.abspath(os.path.join(_THIS_DIR, "..", "lab2"))
if _LAB1_DIR not in sys.path:
    sys.path.append(_LAB1_DIR)

if _LAB2_DIR not in sys.path:
    sys.path.append(_LAB2_DIR)

from TritimiusCipher import TrithemiusCipher  # type: ignore
from Alphabet import TelegraphAlphabet  # type: ignore
import c_block  # type: ignore

# Глобальный алфавит
_ALPH = TelegraphAlphabet()

# ------------------------- Базовые операции над символами/строками -------------------------

def block2num(block_in: str):
    """ Переводит строку из 4 букв в одно число """
    out = 0
    if len(block_in) == 4:
        pos = 1
        tmp = c_block.text2array(block_in)
        for i in reversed(range(4)):
            out = pos * tmp[i] + out
            pos = 32 * pos
    else:
        out = "input_error"
    return out

def num2block(num_in: int):
    """ Переводит число в строку из 4 символов """
    tmp = [None] * 4
    rem = num_in
    for i in range(4):
        tmp[3 - i] = rem % 32
        rem = rem // 32
    return c_block.array2text(tmp)

# block1 = "АБВГ"
# block2 = "_ЯЗЬ"
# block3 = "ЯЯЯЯ"
# answer1 = block2num(block1)
# answer2 = block2num(block2)
# answer3 = block2num(block3)
# b1 = num2block(answer1)
# b2 = num2block(answer2)
# b3 = num2block(answer3)
# print(f"in: {answer1}, out: {b1}")
# print(f"in: {answer2}, out: {b2}")
# print(f"in: {answer3}, out: {b3}")

def dec2bin(num_in: int):
    """ Переводит число из десятичной в двоичную систему """
    rem = num_in
    out = [None] * 20
    for i in range(20):
        out[19 - i] = rem % 2
        rem = rem // 2
    return out

def bin2dec(bin_in):
    """ Перевоит число из двоичной в десятичную систему """
    out = 0
    for i in range(20):
        out = 2 * out + bin_in[i]
    return out

# in1 = 34916
# in2 = 32028
# in3 = 1048575
# bin1 = dec2bin(in1)
# bin2 = dec2bin(in2)
# bin3 = dec2bin(in3)
# print(f"in: {bin1}, out: {bin2dec(bin1)}")
# print(f"in: {bin2}, out: {bin2dec(bin2)}")
# print(f"in: {bin3}, out: {bin2dec(bin3)}")

def initilize_PRNG(seed_in):
    """ Я ХЗ че это, но на выходе 4 раза по 12 буковок """
    cnst = ["ПЕРВОЕ_АКТЕРСТВО", "ВТОРОЙ_ДАЛЬТОНИК", "ТРЕТЬЯ_САДОВНИЦА", "ЧЕТВЕРТЫЙ_ГОБЛИН"]
    value = [None] * 4
    out = [None] * 4
    cblock = c_block.CBlock()
    for i in range(4):
        value[i] = cblock.c_block([cnst[i], seed_in], 16)
    secret = cblock.c_block(value, 16)
    for i in range(4):
        tmp = value[i]
        TMP = ""
        for j in range(4):
            tmp = c_block.add_txt(tmp, cnst[j])
            TMP = TMP + cblock.c_block([tmp, secret], 4)
            tmp = c_block.add_txt(tmp, TMP)
        out[i] = TMP[0:12]
    return out

# IN1 = "ХОРОШО_БЫТЬ_ВАМИ"
# print(initilize_PRNG(IN1))

def LCG_NEXT(state_in, coefs_in):
    a, c, m = coefs_in
    return (a * state_in + c) % m

# LCG_SET1 = [723482, 8677, 983609]
# LCG_SEED1 = block2num("ЛУЛУ")
# OUT1 = LCG_NEXT(LCG_SEED1, LCG_SET1)
# O_TXT1 = num2block(OUT1)
# out = [None] * 10
# o_txt = [None] * 10
# out[0] = OUT1
# o_txt[0] = O_TXT1 
# for i in range(9):
#     out[i+1] = LCG_NEXT(out[i], LCG_SET1)
#     o_txt[i+1] = num2block(out[i+1]) 
# print(o_txt)

def compose_num(num1_in, num2_in, cont_in):
    arr1 = dec2bin(num1_in)
    arr2 = dec2bin(num2_in)
    arr3 = dec2bin(cont_in)
    arr = [None] * 20
    for i in range(20):
        arr[i] = (arr1[i] * arr3[i]) + (arr2[i] * ((1 + arr3[i]) % 2))
    return bin2dec(arr) 

# tst1 = 1231
# tst2 = 723482
# cont1 = 448033
# print(compose_num(tst1, tst2, cont1))

def CT_LCG_NEXT(state_in, set_in):
    first = LCG_NEXT(state_in[0], set_in[0])
    second = LCG_NEXT(state_in[1], set_in[1])
    control = LCG_NEXT(state_in[2], set_in[2])
    out = compose_num(first, second, control)
    return out, first, second, control

def seed2nums(array_in):
    l = len(array_in)
    out = [None] * l
    for i in range(l):
        out[i] = block2num(array_in[i])
    return out

# s1 = seed2nums(["АПЧХ", "ЧПОК", "ШУРА"])
# set0 = [723482, 8677, 983609] 
# set1 = [252564, 9109, 961193] 
# set2 = [357630, 8971, 948209]
# set = [set0, set1, set2]    
# out10 = CT_LCG_NEXT(s1, set)
# t_out10 = num2block(out10[0])
# out = [None] * 10
# t_out = [None] * 10
# out[0] = out10
# t_out[0] = t_out10
# for i in range(9):
#     out[i+1] = CT_LCG_NEXT(out[i], set)
#     t_out[i+1] = num2block(out[i+1][0])

# print(t_out)

def C_CT_LSG_NEXT(init_flag, state_in, seed_in, set_in):
    out = "something_wrong"
    stream = ""
    check = 0
    state = [None] * 4
    if init_flag == "up":
        init = initilize_PRNG(seed_in)
        for i in range(4):
            state[i] = seed2nums([init[i][0:4], init[i][4:8], init[i][8:12]])
            check = 1
    elif init_flag == "down":
        state = state_in
        check = 1
    
    if check:
        for j in range(4):
            tmp = 0
            sign = 1
            for i in range(4):
                T = CT_LCG_NEXT(state[i], set_in[j])
                state[i] = T
                tmp = (1048576 + sign * T[0] + tmp) % 1048576
                sign = -sign
            stream = stream + num2block(tmp)

    return stream, state

# set1 = [None] * 3
# set1[0] = [252564, 9109, 961193]
# set1[1] = [252564, 9109, 961193]
# set1[2] = [723482, 8677, 983609]
# SET_0 = set1

# # set2
# set2 = [None] * 3
# set2[0] = [51190, 7927, 990711]
# set2[1] = [51190, 7927, 990711]
# set2[2] = [549234, 6949, 939683]
# SET_1 = set2

# # set3
# set3 = [None] * 3
# set3[0] = [227796, 5107, 981875]
# set3[1] = [227796, 5107, 981875]
# set3[2] = [167490, 9871, 809137]
# SET_2 = set3

# # set4
# set4 = [None] * 3
# set4[0] = [357630, 8971, 948209]
# set4[1] = [357630, 8971, 948209]
# set4[2] = [73335, 6779, 1014784]
# SET_3 = set4

# SET = [SET_0, SET_1, SET_2, SET_3]
# seed = "АБВГДЕЖЗИЙКЛМНОП"

# intern0 = [None] * 4
# out0, intern0 = C_CT_LSG_NEXT("up", -1, seed, SET)

# # print(out0)
# # print(intern)
# out = [None] * 8
# out[0] = out0
# intern = [None] * 8
# intern[0] = intern0

# for i in range(7):
#     out[i+1], intern[i+1] = C_CT_LSG_NEXT("down", intern[i], -1, SET)

# print(out)
# print("====================")
# print(intern)