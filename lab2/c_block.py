from typing import Callable, Iterable, List, Sequence, Tuple
import os
import sys

# Корректный импорт модулей ЛР1
_THIS_DIR = os.path.dirname(__file__)
_LAB1_DIR = os.path.abspath(os.path.join(_THIS_DIR, "..", "lab1"))
if _LAB1_DIR not in sys.path:
    sys.path.append(_LAB1_DIR)

from TritimiusCipher import TrithemiusCipher  # type: ignore
from Alphabet import TelegraphAlphabet  # type: ignore

# Глобальный алфавит
_ALPH = TelegraphAlphabet()

# ------------------------- Базовые операции над символами/строками -------------------------

def add_s(s1_in: str, s2_in: str, alphabet: TelegraphAlphabet = _ALPH) -> str:
    """Сложение двух символов телеграфного алфавита по модулю 32"""
    v1 = alphabet.get_value_by_char(s1_in.upper())
    v2 = alphabet.get_value_by_char(s2_in.upper())
    return alphabet.get_char_by_value((v1 + v2 + 1) % 32).char


def sub_s(s1_in: str, s2_in: str, alphabet: TelegraphAlphabet = _ALPH) -> str:
    """Вычитание двух символов (обратная операция к нашему add_s с +1)"""
    v1 = alphabet.get_value_by_char(s1_in.upper())
    v2 = alphabet.get_value_by_char(s2_in.upper())
    return alphabet.get_char_by_value((32 + v1 - v2 - 1) % 32).char


def _bin_op_txt(
    t1_in: str,
    t2_in: str,
    op_char: Callable[[str, str, TelegraphAlphabet], str],
    alphabet: TelegraphAlphabet = _ALPH,
) -> str:
    """Общий помощник для посимвольных операций над строками.
    Перекрывающаяся часть обрабатывается посимвольно,
    хвост более длинной строки дописывается как есть.
    """
    out: List[str] = []
    m = min(len(t1_in), len(t2_in))
    t_in = t1_in if len(t1_in) > len(t2_in) else t2_in

    for i in range(m):
        out.append(op_char(t1_in[i], t2_in[i], alphabet))

    if len(t_in) > m:
        out.append(t_in[m:])

    return "".join(out)


def add_txt(t1_in: str, t2_in: str, alphabet: TelegraphAlphabet = _ALPH) -> str:
    """Посимвольное сложение двух строк по модулю 32 с дописыванием хвоста"""
    return _bin_op_txt(t1_in, t2_in, lambda a, b, A: add_s(a, b, A), alphabet)


def sub_txt(t1_in: str, t2_in: str, alphabet: TelegraphAlphabet = _ALPH) -> str:
    """Посимвольное вычитание двух строк по модулю 32 с дописыванием хвоста"""
    return _bin_op_txt(t1_in, t2_in, lambda a, b, A: sub_s(a, b, A), alphabet)


def text2array(text: str, alphabet: TelegraphAlphabet = _ALPH) -> List[int]:
    return [alphabet.get_value_by_char(ch.upper()) for ch in text]


def array2text(arr: Sequence[int], alphabet: TelegraphAlphabet = _ALPH) -> str:
    return "".join(alphabet.get_char_by_value(v & 0b11111).char for v in arr)


# --------------------------- Ядро односторонней функции ---------------------------

def core_trithemius(IN_prime: str, IN_aux: str) -> str:
    """Ядро на основе полиалфавитного шифра Тритемуса

    В mathcad core_Trithemus(IN_prime, IN_aux) вызывает frw_poly_Trithemus
    с plaintext=IN_aux и key=IN_prime. Здесь это encrypt_poly(IN_aux, IN_prime).

    Требование: оба входа ровно 16 символов.
    """
    if len(IN_prime) == 16 and len(IN_aux) == 16:
        return TrithemiusCipher.encrypt_poly(IN_aux, IN_prime)
    return "input_error"


# ------------------------------ Вспомогательные блоки ------------------------------

def confuse(IN1: str, IN2: str, alphabet: TelegraphAlphabet = _ALPH) -> str:
    """Сделать преобразование менее однозначным внутри C-блока

    Для 16-символьных строк IN1, IN2:
      - arr1, arr2 — массивы значений 0..31
      - для i = 0..15:
          if arr1[i] > arr2[i]: arr1[i] = (arr1[i] + i) mod 32
          else:                 arr1[i] = (arr2[i] + i) mod 32
      - tmp = array2text(arr1)
      - out = add_txt(add_txt(tmp, IN1), IN2)
    """
    if not (len(IN1) == 16 and len(IN2) == 16):
        return "input_error"

    arr1 = text2array(IN1, alphabet)
    arr2 = text2array(IN2, alphabet)

    for i in range(16):
        if arr1[i] > arr2[i]:
            arr1[i] = (arr1[i] + i) % 32
        else:
            arr1[i] = (arr2[i] + i) % 32

    tmp = array2text(arr1, alphabet)
    return add_txt(add_txt(tmp, IN1, alphabet), IN2, alphabet)


def mixinputs(IN: Sequence[str], alphabet: TelegraphAlphabet = _ALPH) -> Tuple[str, str, str, str]:
    """Перемешивание входов (4 по 16)"""
    if len(IN) != 4 or not all(len(x) == 16 for x in IN):
        return ("input_error",) * 4

    in1, in2, in3, in4 = IN
    out1 = add_txt(in1, in2, alphabet)
    out2 = sub_txt(in1, in2, alphabet)
    out3 = add_txt(out2, add_txt(in3, in4, alphabet), alphabet)
    out4 = add_txt(out1, sub_txt(in3, in4, alphabet), alphabet)
    return out1, out2, out3, out4


def compress(IN_16: str, out_n: int | str, alphabet: TelegraphAlphabet = _ALPH) -> str:
    """Урезать 16-символьный вход до out_n ∈ {16, 8, 4}"""
    if len(IN_16) != 16:
        return "input_error"

    if isinstance(out_n, str):
        try:
            out_n = int(out_n)
        except ValueError:
            return "input_error"

    if out_n not in (4, 8, 16):
        return "input_error"

    if out_n == 16:
        return IN_16

    a1 = IN_16[0:4]
    a2 = IN_16[4:8]
    a3 = IN_16[8:12]
    a4 = IN_16[12:16]

    if out_n == 8:
        a13 = a1 + a3
        a24 = a2 + a4
        return add_txt(a13, a24, alphabet)

    # out_n == 4
    a13 = sub_txt(a1, a3, alphabet)
    a24 = sub_txt(a2, a4, alphabet)
    return add_txt(a13, a24, alphabet)


def reverse_str(IN: str) -> str:
    return IN[::-1]


def blocks_mix(IN1: str, IN2: str, alphabet: TelegraphAlphabet = _ALPH) -> Tuple[str, str]:
    """Перемешивание двух 16-символьных блоков (возвращает 2 блока).
    По mathcad: reverse_str(IN1) -> затем out0 = add_txt, out1 = sub_txt.
    """
    if not (len(IN1) == 16 and len(IN2) == 16):
        return ("input_error", "input_error")

    rev1 = reverse_str(IN1)
    out0 = add_txt(rev1, IN2, alphabet)
    out1 = sub_txt(rev1, IN2, alphabet)
    return out0, out1


def block_mask(IN: str, CONST: str, alphabet: TelegraphAlphabet = _ALPH) -> str:
    """Наложение константы на блок (эвристическая интерпретация формулы из mathcad)."""
    if not (len(IN) == 16 and len(CONST) == 16):
        return "input_error"

    arr = text2array(IN, alphabet)
    con = text2array(CONST, alphabet)
    out: List[int] = [0] * 16

    for i in range(16):
        rhs = (con[i] + i) % 32
        if arr[i] < rhs:
            out[i] = (64 - ((con[i] - i) % 32)) % 32
        else:
            out[i] = (arr[i] + i) % 32

    return array2text(out, alphabet)


# ----------------------------------- C-блок -----------------------------------
class CBlock:
    """C-блок с использованием ядра односторонней функции.

    Интерфейс: c_block(in_arr, out_size, cypher_core)
      - in_arr: последовательность из r блоков по 16 символов (r ∈ N, r >= 1)
      - out_size: 4, 8 или 16 (число символов на выходе)
      - cypher_core: функция ядра, например core_trithemius(INp, INa) -> 16 симв.
    """

    # Базовые константы (4x16) из mathcad
    C_INIT = [
        "________________",
        "ПРОЖЕКТОР_ЧЕПУХИ",
        "КОЛЫХАТЬ_ПАРОДИЮ",
        "КАРМАННЫЙ_АТАМАН",
    ]

    def __init__(self, alphabet: TelegraphAlphabet | None = None) -> None:
        self.alphabet = alphabet if alphabet is not None else _ALPH

    def c_block(self, in_arr: Sequence[str], out_size: int | str) -> str:
        """C-блок с фиксированным ядром core_trithemius.

        in_arr — массив строк, где каждый элемент либо пустая строка "", либо ровно 16 символов.
        Пустые элементы трактуются как отсутствие данных (no-op) для соответствующего Ci.
        """
        # Проверка входов
        if not in_arr:
            return "input_error"
        # Допускаем длину элемента 0 (пустая строка) или 16, иначе ошибка
        if any(len(x) not in (0, 16) for x in in_arr):
            return "input_error"

        # 1) Наложим входы на константы (pos-wise add_txt)
        C = list(self.C_INIT)
        for i, blk in enumerate(in_arr):
            if len(blk) == 16:
                C[i % 4] = add_txt(C[i % 4], blk, self.alphabet)
            # если blk пустой — пропускаем (no-op)

        # 2) Перемешивание входов
        o1, o2, o3, o4 = mixinputs(C, self.alphabet)
        if "input_error" in (o1, o2, o3, o4):
            return "input_error"

        # Обозначим согласно Mathcad-псевдокоду: после mixinputs(C)
        # C0 = o1, C1 = o2, C2 = o3, C3 = o4
        C0, C1, C2, C3 = o1, o2, o3, o4

        # 3) Вызовы ядра (ядро — одностороннее преобразование 16 -> 16)
        # По требованиям: tmp1 = core(C0, C2), tmp2 = core(C3, C1)
        tmp1 = core_trithemius(C0, C2)
        tmp2 = core_trithemius(C3, C1)
        if "input_error" in (tmp1, tmp2):
            return "input_error"

        # 4) Запутывание и финальный проход через ядро
        tmp3 = confuse(tmp1, tmp2, self.alphabet)
        if tmp3 == "input_error":
            return tmp3

        out16 = core_trithemius(tmp3, tmp1)
        if out16 == "input_error":
            return out16

        # 5) Урезаем
        return compress(out16, out_size, self.alphabet)


# ------------------------------ Макрокомпрессия (64->state) ------------------------------

def macrocompression(IN: str, STATE: str) -> str:
    """Макрокомпрессия одного 64-символьного блока в состояние (80 символов).

    IN    — входной блок данных (64 символа)
    STATE — текущее состояние (80 символов = A||B||C||D||E по 16)
    Возвращает новое состояние (80 символов).
    """
    if len(IN) != 64 or len(STATE) != 80:
        return "input_error"

    # Разбивка на блоки по 16
    Ain, Bin, Cin, Din = IN[0:16], IN[16:32], IN[32:48], IN[48:64]
    A, B, C, D, E = STATE[0:16], STATE[16:32], STATE[32:48], STATE[48:64], STATE[64:80]

    # Начальная свертка входа со стейтом
    A = add_txt(Ain, A)
    B = add_txt(Bin, B)
    C = add_txt(Cin, C)
    D = add_txt(Din, D)

    # Константа (16 символов)
    CON = "ААААЯЯЯЯААЯЯААЯЯ"
    cblock = CBlock()

    # 12 раундов легкой диффузии, опираясь только на разрешенные примитивы
    for i in range(12):
        t1 = core_trithemius(A, C)            # 16
        t2 = core_trithemius(D, B)            # 16
        t3 = confuse(t1, t2)              # 16

        # Обновление состояний
        A = add_txt(A, t3)                # 16
        B = block_mask(B, CON)            # 16
        C, D = blocks_mix(C, D)           # по 16
        E = add_txt(E, cblock.c_block([t1, t2], 16))  # 16

        # Сдвиг константы для маскирования
        CON = add_txt(CON, "ААААЯЯЯЯААЯЯААЯЯ")

    # Новое состояние — конкатенация по 16 символов
    return A + B + C + D + E


# ------------------------------ Пэддинг (Merkle–Damgård) ------------------------------

def pad_MD(IN: str) -> str:
    """Подложка: дополнение под кратность 64 символам символом '_' (код 31)."""
    L = len(IN)
    rem = 64 - (L % 64)
    if rem == 64:
        return IN
    return IN + ("_" * rem)


# ------------------------------ Хеш-функция (Merkle–Damgård) ------------------------------

def MerDam_hash(MSG: str) -> str:
    """Хеш-функция на основе структуры Меркла–Дамгора

    - Внутренняя компрессия: macrocompression (64 символа -> новое состояние 80)
    - Начальное состояние: 80 символов '_' (пустое состояние)
    - Дайджест: конкатенация C_block(A), C_block(B), C_block(C), C_block(D)
      (каждый — 16 символов), итого 64 символа.
    """
    DATA = pad_MD(MSG)
    n_blocks = len(DATA) // 64

    # Начальное состояние (A..E = '_'*16)
    A = B = C = D = E = "_" * 16

    for i in range(n_blocks):
        blk = DATA[i * 64:(i + 1) * 64]
        state = macrocompression(blk, A + B + C + D + E)
        if state == "input_error" or len(state) != 80:
            return "input_error"
        A, B, C, D, E = state[0:16], state[16:32], state[32:48], state[48:64], state[64:80]

    cblock = CBlock()
    p1 = cblock.c_block([A], 16)
    p2 = cblock.c_block([B], 16)
    p3 = cblock.c_block([C], 16)
    p4 = cblock.c_block([D], 16)

    if "input_error" in (p1, p2, p3, p4):
        return "input_error"

    return p1 + p2 + p3 + p4
