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

from c_block import MerDam_hash, add_txt  # type: ignore
from LinearCongruentialGenerator import block2num, dec2bin, bin2dec, num2block # type: ignore
from Feistel import frw_Feistel, inv_Feistel, produce_round_keys  # type: ignore
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
_file_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(_file_dir, "inp.txt"), 'r', encoding='utf-8') as file:
    INPUT_ARRAY = file.readlines()

# # Удаляем символы \n из каждой строки
INPUT_ARRAY = [line.rstrip('\n') for line in INPUT_ARRAY]
# q = msg2bin(INPUT_ARRAY[3])
# print(bin2msg(q))

ASSOCDATA_ARRAY = [
    ["ВА", "АЛИСА__А", "БОБ____А", "КОТОПОЕЗД"],
    ["ВБ", "АЛИСА_АХ", "БОБ___ОЧ", "ЕГИПТЯНИН"],
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
    data = list(DATA_IN)
    iv = add_txt("_" * 16, (IV_in + "_" * 16)[:16])
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
    iv = p[32:48]
    L = 0
    for i in range(5):
        t = length[i]
        l = sym2num(t)
        L = 32 * L + l
    L = L // 5
    message = p[48:48+L]
    mac = p[48+L:M]
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
    ml = min(len(A_IN), len(B_IN))
    n4 = ml // 4
    out = ""
    C = [None] * 80
    for i in range(n4):
        a = A_IN[i*4:i*4+4]
        b = B_IN[i*4:i*4+4]
        A = dec2bin(block2num(a))
        B = dec2bin(block2num(b))
        for j in range(20):
            C[j] = (A[j] + B[j]) % 2
        c = bin2dec(C)
        out = out + num2block(c)
    pos = n4 * 4
    longer = A_IN if len(A_IN) > len(B_IN) else B_IN
    if len(longer) > pos:
        out += longer[pos:]
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

def frw_CFB(MSG_IN, IV_IN, keyset, mac_in):
    """
    Прямое CFB-шифрование.
    keyset — список раундовых ключей (produce_round_keys).
    mac_in:  0 -> шифротекст,  1 -> шифротекст+MAC(16),  -1 -> только MAC(16).
    """
    R = len(keyset) - 2
    m = len(MSG_IN) // 16
    if m == 0:
        return ""

    feedback = IV_IN
    out = ""
    cont = "_" * 16

    for i in range(m):
        inp = MSG_IN[i*16:(i+1)*16]
        cont = textor(inp, cont)
        keystream = frw_Feistel(feedback, keyset, R)
        feedback = textor(inp, keystream)
        out += feedback

    keystream = frw_Feistel(feedback, keyset, R)
    mac = textor(cont, keystream)

    if mac_in == 0:
        return out
    elif mac_in == 1:
        return out + mac
    else:
        return mac


def inv_CFB(MSG_IN, IV_IN, keyset, mac_in):
    """
    Обратное CFB-расшифрование.
    mac_in:  0 -> открытый текст,  1 -> открытый текст+cont(16),  -1 -> только cont(16).
    """
    R = len(keyset) - 2
    m = len(MSG_IN) // 16
    feedback = IV_IN
    out = ""
    cont = "_" * 16

    loop_end = m if mac_in == 0 else m - 1
    for i in range(loop_end):
        inp = MSG_IN[i*16:(i+1)*16]
        keystream = frw_Feistel(feedback, keyset, R)
        feedback = inp
        text = textor(inp, keystream)
        cont = textor(cont, text)
        out += text

    if mac_in != 0:
        mac = MSG_IN[(m-1)*16:m*16]
        keystream = frw_Feistel(feedback, keyset, R)
        text = textor(mac, keystream)
        cont = textor(cont, text)
        if mac_in == 1:
            out = out + cont
        else:
            out = cont

    return out


def _concat_ad(data_list):
    """Конкатенация ассоциированных данных (первые 4 элемента data)."""
    return "".join(data_list[:4])


def EAX_CFB_frw(PACKET_IN, CMAC_IN, keyset, SEC_IN, onlymac):
    """
    EAX-CFB зашифрование.
    PACKET_IN: [data, iv, msg, mac]
    onlymac=1 -> msg остаётся открытым, вычисляется только MAC
    onlymac=0 -> msg шифруется + MAC
    """
    data = PACKET_IN[0]
    IV_IN = PACKET_IN[1]
    MSG_IN = PACKET_IN[2]

    tmp = _concat_ad(data)
    sec_tmp = SEC_IN + tmp
    while len(sec_tmp) % 16 != 0:
        sec_tmp += "_"

    CIV = frw_CFB(sec_tmp, IV_IN, keyset, -1)

    if onlymac == 1:
        tmp2 = frw_CFB(MSG_IN, CIV, keyset, -1)
        MAC = textor(textor(tmp2, CIV), CMAC_IN)
        MSG = MSG_IN
    else:
        tmp2 = frw_CFB(MSG_IN, CIV, keyset, 1)
        m = tmp2[len(MSG_IN):]
        MAC = textor(textor(m, CIV), CMAC_IN)
        MSG = tmp2[:len(MSG_IN)]

    return [data, IV_IN, MSG, MAC]


def EAX_CFB_inv(PACKET_IN, keyset, SEC_IN, onlymac):
    """
    EAX-CFB расшифрование.
    PACKET_IN: [data, iv, msg, mac]
    """
    data = PACKET_IN[0]
    IV_IN = PACKET_IN[1]
    MSG_IN = PACKET_IN[2]
    MAC_IN = PACKET_IN[3]

    tmp = _concat_ad(data)

    ad_padded = tmp
    while len(ad_padded) % 16 != 0:
        ad_padded += "_"
    CMAC = frw_CFB(ad_padded, SEC_IN, keyset, -1)

    sec_tmp = SEC_IN + tmp
    while len(sec_tmp) % 16 != 0:
        sec_tmp += "_"
    CIV = frw_CFB(sec_tmp, IV_IN, keyset, -1)

    if onlymac == 1:
        tmp2 = frw_CFB(MSG_IN, CIV, keyset, -1)
        MAC = textor(MAC_IN, textor(textor(tmp2, CIV), CMAC))
        MSG = MSG_IN
    else:
        cont = textor(textor(MAC_IN, CIV), CMAC)
        tmp2 = inv_CFB(MSG_IN + cont, CIV, keyset, 1)
        MSG = tmp2[:len(MSG_IN)]
        mac_computed = tmp2[len(MSG_IN):]
        MAC = mac_computed

    return [data, IV_IN, MSG, MAC]

def insert(STREAM_IN, s, m):
    """Вставка бита в поток (имитация ошибки канала)."""
    return STREAM_IN[:m] + [s] + STREAM_IN[m:]

class EAXSession:
    """Сеанс EAX-CFB."""

    def __init__(self, AD, MASTER_KEY, nonce):
        """
        AD:         [type(2), sender(8), receiver(8), session(9)]
        MASTER_KEY: мастер-ключ (16 символов)
        nonce:      одноразовое значение (16 символов)
        """
        self.AD = AD
        self.edge = AD[0]
        self.sender = AD[1]
        self.receiver = AD[2]
        self.session_id = AD[3] if len(AD) > 3 else "_" * 9

        self.keyset = produce_round_keys(MASTER_KEY, 8, None)

        t1 = (self.sender + self.receiver + "_" * 16)[:16]
        t2 = (self.edge + self.sender + self.receiver + self.session_id + "_" * 16)[:16]

        self.secret = frw_CFB(t2, t1, self.keyset, -1)

        combined = add_txt(
            (t1 + t2)[:16],
            (nonce + "_" * 16)[:16],
        )
        self.IVO = combined[:12]

        ad_concat = _concat_ad(AD)
        while len(ad_concat) % 16 != 0:
            ad_concat += "_"
        self.data_mac = frw_CFB(ad_concat, self.secret, self.keyset, -1)

        self.msg_counter = -1

    def _next_iv(self):
        """IV = IVO(12 символов) + num2block(counter)(4 символа) = 16 символов."""
        self.msg_counter += 1
        return self.IVO + num2block(self.msg_counter)

    def send(self, messages):
        """Зашифровать и передать массив сообщений -> список битовых потоков."""
        transmissions = []
        for msg in messages:
            IV = self._next_iv()
            pkt = prepare_packet(
                [self.edge, self.sender, self.receiver, self.session_id],
                IV, msg,
            )
            if self.edge == "В_":
                transmissions.append(transmit(pkt))
            elif self.edge == "ВА":
                enc = EAX_CFB_frw(pkt, self.data_mac, self.keyset, self.secret, 1)
                transmissions.append(transmit(enc))
            elif self.edge == "ВБ":
                enc = EAX_CFB_frw(pkt, self.data_mac, self.keyset, self.secret, 0)
                transmissions.append(transmit(enc))
        return transmissions

    def receive(self, streams):
        """Принять и расшифровать массив битовых потоков -> список результатов."""
        results = []
        for stream in streams:
            pkt = recieve(stream)
            rtype = pkt[0][0]

            try:
                if rtype == "ВБ":
                    dec = EAX_CFB_inv(pkt, self.keyset, self.secret, 0)
                    msg_out = unpad_message(dec[2])
                    mac_ok = (dec[3] == "" or all(c == 'А' for c in dec[3]))
                    results.append({"status": "OK" if mac_ok else "MAC_ERROR", "message": msg_out})
                elif rtype == "ВА":
                    dec = EAX_CFB_inv(pkt, self.keyset, self.secret, 1)
                    msg_out = unpad_message(dec[2])
                    mac_ok = (dec[3] == "" or all(c == 'А' for c in dec[3]))
                    results.append({"status": "OK" if mac_ok else "MAC_ERROR", "message": msg_out})
                elif rtype == "В_":
                    msg_out = unpad_message(pkt[2])
                    results.append({"status": "OK", "message": msg_out})
                else:
                    results.append({"status": "ERROR", "message": ""})
            except Exception:
                results.append({"status": "ERROR", "message": ""})
        return results

# =====================================================================
#  ТЕСТЫ
# =====================================================================

if __name__ == "__main__":

    MASTER_KEY = "СЕАНСОВЫЙ_КЛЮЧИК"
    IV1 = "АЛИСА_УМЕЕТ_ПЕТЬ"
    IV2 = "БОБ_НЕМНОГО_ПЬЯН"

    TST = ("ГАРРИ_С_ОТКРЫТЫМ_РТОМ_СМОТРЕЛ_НА_СЕМЕЙНОЕ_ХРАНИЛИЩЕ_ТЧК_"
           "У_НЕГО_БЫЛО_ТАК_МНОГО_ВОПРОСОВ_ЗПТ_ЧТО_ОН_ДАЖЕ_НЕ_ЗНАЛ_ЗПТ_"
           "С_КАКОГО_ИМЕННО_НАЧАТЬ_ТЧК_МАКГОНАГАЛЛ_СТОЯЛА_У_ДВЕРИ_И_"
           "НАБЛЮДАЛА_ЗА_МАЛЬЧИКОМ_ТЧК")
    while len(TST) % 16 != 0:
        TST += "_"

    keyset = produce_round_keys(MASTER_KEY, 8, None)

    passed = 0
    failed = 0

    def check(name, condition):
        global passed, failed
        if condition:
            passed += 1
            print(f"  [OK]   {name}")
        else:
            failed += 1
            print(f"  [FAIL] {name}")

    # ==================================================================
    print("=" * 64)
    print("  ТЕСТ 1 : frw_CFB / inv_CFB")
    print("=" * 64)

    # --- mac_in = 1 (шифротекст + имитовставка) ---
    E1 = frw_CFB(TST, IV1, keyset, 1)
    D1 = inv_CFB(E1, IV1, keyset, 1)
    print(f"\n  mac_in=1 : текст {len(TST)} -> шифр {len(E1)} -> расшифр {len(D1)} симв.")
    print(f"  MAC (последний блок) = '{E1[len(TST):]}'")
    print(f"  cont после расшифр.  = '{D1[-16:]}'")
    check("расшифр[:-16] == исходный текст", D1[:-16] == TST)
    check("cont = все 'А' (целостность OK)", all(c == 'А' for c in D1[-16:]))

    # --- mac_in = 0 (без имитовставки) ---
    E0 = frw_CFB(TST, IV1, keyset, 0)
    D0 = inv_CFB(E0, IV1, keyset, 0)
    print(f"\n  mac_in=0 : текст {len(TST)} -> шифр {len(E0)} -> расшифр {len(D0)} симв.")
    check("расшифр == исходный текст", D0 == TST)

    # --- mac_in = -1 (только MAC) ---
    MAC_only = frw_CFB(TST, IV1, keyset, -1)
    print(f"\n  mac_in=-1: MAC = '{MAC_only}'  (длина {len(MAC_only)})")
    check("MAC == последний блок шифротекста", MAC_only == E1[len(TST):])

    # --- другой IV ---
    E_iv2 = frw_CFB(TST, IV2, keyset, 1)
    D_iv1 = inv_CFB(E_iv2, IV1, keyset, 1)
    D_iv2 = inv_CFB(E_iv2, IV2, keyset, 1)
    print(f"\n  Зашифровано IV2, расшифровка IV1: совпадение = {D_iv1[:-16] == TST}")
    print(f"  Зашифровано IV2, расшифровка IV2: совпадение = {D_iv2[:-16] == TST}")
    check("правильный IV расшифровывает верно", D_iv2[:-16] == TST)
    check("неправильный IV не расшифровывает", D_iv1[:-16] != TST)

    # ==================================================================
    print("\n" + "=" * 64)
    print("  ТЕСТ 2 : EAX_CFB_frw / EAX_CFB_inv")
    print("=" * 64)

    AD = ["ВБ", "АЛИСА_АХ", "БОБ___ОЧ", "ЕГИПТЯНИН"]
    SEC = ("ПОКА_ЕЩЕ_НЕВАКНО" + "_" * 16)[:16]

    ad_str = _concat_ad(AD)
    while len(ad_str) % 16 != 0:
        ad_str += "_"
    cadmac = frw_CFB(ad_str, SEC, keyset, -1)
    print(f"\n  AD     = {AD}")
    print(f"  cadmac = '{cadmac}'")

    # --- onlymac = 0 (шифрование + MAC) ---
    pkt = prepare_packet(list(AD), IV1, TST)
    orig = unpad_message(pkt[2])

    enc = EAX_CFB_frw(pkt, cadmac, keyset, SEC, 0)
    dec = EAX_CFB_inv(enc, keyset, SEC, 0)
    dec_msg = unpad_message(dec[2])
    mac_zero = all(c == 'А' for c in dec[3])
    print(f"\n  onlymac=0: MAC = '{dec[3]}'  (все А = {mac_zero})")
    check("onlymac=0: расшифр == оригинал", dec_msg == orig)
    check("onlymac=0: MAC = все А (целостность)", mac_zero)

    # --- onlymac = 1 (только MAC, текст открыт) ---
    enc1 = EAX_CFB_frw(pkt, cadmac, keyset, SEC, 1)
    dec1 = EAX_CFB_inv(enc1, keyset, SEC, 1)
    dec1_msg = unpad_message(dec1[2])
    mac1_zero = all(c == 'А' for c in dec1[3])
    print(f"\n  onlymac=1: MAC = '{dec1[3]}'  (все А = {mac1_zero})")
    check("onlymac=1: текст == оригинал", dec1_msg == orig)
    check("onlymac=1: MAC = все А (целостность)", mac1_zero)

    # ==================================================================
    print("\n" + "=" * 64)
    print("  ТЕСТ 3 : EAXSession  (отправка / приём)")
    print("=" * 64)

    NONCE = ("СИМУЛЯТОР_КВАНТЫ_" + "_" * 16)[:16]

    # --- тип ВБ ---
    print(f"\n  --- Тип ВБ (шифрование + MAC) ---")
    s_vb = EAXSession(AD, MASTER_KEY, NONCE)
    streams_vb = s_vb.send([TST])
    print(f"  Отправлено: {len(streams_vb[0])} бит")

    r_vb = EAXSession(AD, MASTER_KEY, NONCE)
    res_vb = r_vb.receive(streams_vb)
    check("ВБ: status == OK", res_vb[0]["status"] == "OK")
    check("ВБ: сообщение совпадает", res_vb[0]["message"] == orig)

    # --- тип ВА ---
    print(f"\n  --- Тип ВА (только MAC, текст открыт) ---")
    AD_A = ["ВА", "АЛИСА__А", "БОБ____А", "КОТОПОЕЗД"]
    s_va = EAXSession(AD_A, MASTER_KEY, NONCE)
    streams_va = s_va.send([TST])
    print(f"  Отправлено: {len(streams_va[0])} бит")

    r_va = EAXSession(AD_A, MASTER_KEY, NONCE)
    res_va = r_va.receive(streams_va)
    check("ВА: status == OK", res_va[0]["status"] == "OK")
    check("ВА: сообщение совпадает", res_va[0]["message"] == orig)

    # --- тип В_ ---
    print(f"\n  --- Тип В_ (без шифрования, без MAC) ---")
    AD_P = ["В_", "АЛИСА_ЯЗ", "БОБ___ЬЬ", "ЩЕГОЛЯНИЕ"]
    s_p = EAXSession(AD_P, MASTER_KEY, NONCE)
    streams_p = s_p.send([TST])
    print(f"  Отправлено: {len(streams_p[0])} бит")

    r_p = EAXSession(AD_P, MASTER_KEY, NONCE)
    res_p = r_p.receive(streams_p)
    check("В_: status == OK", res_p[0]["status"] == "OK")
    check("В_: сообщение совпадает", res_p[0]["message"] == orig)

    # ==================================================================
    print("\n" + "=" * 64)
    print("  ТЕСТ 4 : ASSOCDATA_ARRAY + INPUT_ARRAY  (все пары)")
    print("=" * 64)

    ncols = min(len(ASSOCDATA_ARRAY), len(INPUT_ARRAY))
    print(f"\n  Пар: {ncols},  сообщений: {len(INPUT_ARRAY)}")

    for i in range(ncols):
        ad_i = ASSOCDATA_ARRAY[i]
        msg_i = INPUT_ARRAY[i]

        sx = EAXSession(ad_i, MASTER_KEY, NONCE)
        stx = sx.send([msg_i])

        rx = EAXSession(ad_i, MASTER_KEY, NONCE)
        resx = rx.receive(stx)
        r = resx[0]
        ok = (r["status"] == "OK" and msg2bin(r["message"]) == msg2bin(msg_i))
        short = (msg_i[:36] + "...") if len(msg_i) > 36 else msg_i
        check(f"[{i}] type={ad_i[0]}  '{short}'", ok)

    # ==================================================================
    print("\n" + "=" * 64)
    print("  ТЕСТ 5 : Один сеанс ВБ, все сообщения подряд")
    print("=" * 64)

    AD_VB = ASSOCDATA_ARRAY[1]
    s2 = EAXSession(AD_VB, MASTER_KEY, NONCE)
    channels = s2.send(INPUT_ARRAY)

    print(f"\n  Отправлено {len(channels)} сообщений  (edge={AD_VB[0]})")
    for i, ch in enumerate(channels):
        print(f"    CH[{i}]: {len(ch):>6d} бит  ({len(ch)//5:>4d} симв.)")

    r2 = EAXSession(AD_VB, MASTER_KEY, NONCE)
    results2 = r2.receive(channels)

    print()
    for i, r in enumerate(results2):
        ok = (r["status"] == "OK" and msg2bin(r["message"]) == msg2bin(INPUT_ARRAY[i]))
        check(f"CH[{i}] recv == orig", ok)

    # ==================================================================
    print("\n" + "=" * 64)
    print("  ТЕСТ 6 : Ошибки канала  (insert бита)")
    print("=" * 64)

    corrupted = list(channels)

    positions = []
    positions.append((0, 0, "заголовок (бит 0)"))
    if len(channels) > 1 and len(channels[1]) > 300:
        positions.append((1, 300, "тело (бит 300)"))
    if len(channels) > 3 and len(channels[3]) > 12:
        positions.append((3, 12, "IV (бит 12)"))

    for idx, pos, desc in positions:
        corrupted[idx] = insert(channels[idx], 1, pos)
        print(f"  CH[{idx}]: вставлен 1 бит -> {desc}")

    r3 = EAXSession(AD_VB, MASTER_KEY, NONCE)
    results3 = r3.receive(corrupted)

    damaged = {idx for idx, _, _ in positions}
    print()
    for i, r in enumerate(results3):
        is_damaged = i in damaged
        label = "повреждён" if is_damaged else "не тронут"
        if is_damaged:
            if r["status"] == "ERROR":
                check(f"CH[{i}] ({label}): ошибка -> status=ERROR", True)
            elif r["status"] == "MAC_ERROR":
                check(f"CH[{i}] ({label}): ошибка -> MAC_ERROR", True)
            else:
                match = (msg2bin(r["message"]) == msg2bin(INPUT_ARRAY[i]))
                check(f"CH[{i}] ({label}): ошибка обнаружена (msg искажено)", not match)
        else:
            match = (r["status"] == "OK" and msg2bin(r["message"]) == msg2bin(INPUT_ARRAY[i]))
            check(f"CH[{i}] ({label}): status=OK, msg совпадает", match)

    # ==================================================================
    print("\n" + "=" * 64)
    print("  ТЕСТ 7 : CFB без EAX  (все сообщения)")
    print("=" * 64)

    print()
    for i, msg in enumerate(INPUT_ARRAY):
        m = pad_message(msg)               # подложка -> кратно 80 бит = 16 симв., чистый алфавит
        enc_t = frw_CFB(m, IV1, keyset, 1)
        dec_t = inv_CFB(enc_t, IV1, keyset, 1)
        ok = (dec_t[:-16] == m)
        mac_t = enc_t[len(m):]
        cont_ok = all(c == 'А' for c in dec_t[-16:])
        dec_msg = unpad_message(dec_t[:-16])
        bits_ok = msg2bin(dec_msg) == msg2bin(msg)
        check(f"MSG[{i}]: {len(m):>4d} симв. -> MAC='{mac_t}', cont={cont_ok}, msg={bits_ok}", ok and cont_ok and bits_ok)

    # ==================================================================
    print("\n" + "=" * 64)
    total = passed + failed
    print(f"  ИТОГО: {passed}/{total} пройдено,  {failed} провалено")
    print("=" * 64)
