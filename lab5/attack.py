"""
=============================================================================
  ПЕНТЕСТИНГ ПРОТОКОЛА EAX-CFB — ФАЙЛ АТАК
  Анализ уязвимостей с использованием CPA/CCA оракулов
=============================================================================

АРХИТЕКТУРА ПРОТОКОЛА (краткий разбор):
  - В_  : открытый канал, нет шифрования, нет MAC
  - ВА  : MAC без шифрования (onlymac=1), сообщение открыто
  - ВБ  : шифрование + MAC (onlymac=0), полная защита

РЕЖИМ CFB (Cipher Feedback):
  Шифртекст[i] = Открытый_текст[i] XOR Feistel(Шифртекст[i-1])
  Обратимость: ошибка в блоке C[i] → ошибка в P[i] того же места
               И полная порча P[i+1]
=============================================================================
"""

import os, sys

# ---------------------------------------------------------------------------
# Настройка путей — адаптируй под свою структуру папок
# ---------------------------------------------------------------------------
_THIS = os.path.dirname(os.path.abspath(__file__))
for _rel in ["../lab1", "../lab2", "../lab3", "../lab4", "../lab5"]:
    _p = os.path.abspath(os.path.join(_THIS, _rel))
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

# Попытка импорта — если папки нет рядом, скрипт всё равно выведет анализ
try:
    from eax import (
        EAXSession, prepare_packet, transmit, recieve,
        textor, frw_CFB, inv_CFB, produce_round_keys,
        pad_message, unpad_message, msg2bin, bin2msg,
        num2sym, sym2num, isSym
    )
    IMPORTS_OK = True
except ImportError as _e:
    IMPORTS_OK = False
    _IMPORT_ERROR = str(_e)

# ---------------------------------------------------------------------------
# Вспомогательные функции вывода
# ---------------------------------------------------------------------------

SEP  = "=" * 72
SEP2 = "-" * 72

def banner(title: str):
    print(f"\n{SEP}")
    print(f"  {title}")
    print(SEP)

def section(title: str):
    print(f"\n{SEP2}")
    print(f"  {title}")
    print(SEP2)

def result(label: str, value, width=30):
    print(f"  {label:<{width}}: {value}")

def ok(msg):  print(f"  [✓] {msg}")
def err(msg): print(f"  [✗] {msg}")
def info(msg):print(f"  [i] {msg}")

# ---------------------------------------------------------------------------
# Фиксированные параметры «честного» сеанса
# ---------------------------------------------------------------------------
MASTER_KEY   = "АБВГДЕЖЗИЙКЛМНОП"   # 16 символов
NONCE        = "РСТУФХЦЧШЩЫЬЭЮЯ_"   # 16 символов

AD_SENDER    = ["ВБ", "АЛИСААА_", "БОБААААА", "СЕССИЯ___"]  # шифрование+MAC
AD_AUTH_ONLY = ["ВА", "АЛИСААА_", "БОБААААА", "СЕССИЯ___"]  # только MAC
AD_OPEN      = ["В_", "АЛИСААА_", "БОБААААА", "СЕССИЯ___"]  # открытый

PLAINTEXT_1  = "ПРИВЕТ"
PLAINTEXT_2  = "СЕКРЕТНОЕ_СООБЩЕНИЕ"

# ===========================================================================
#  АТАКА 0: Проверка работоспособности среды
# ===========================================================================

def attack0_sanity():
    banner("АТАКА 0: Проверка работоспособности среды")

    if not IMPORTS_OK:
        err(f"Импорт не удался: {_IMPORT_ERROR}")
        info("Поместите attack.py рядом с eax.py и зависимостями (lab1–lab4)")
        info("Далее будет показан статический анализ без запуска кода")
        return False

    try:
        alice = EAXSession(AD_SENDER, MASTER_KEY, NONCE)
        bob   = EAXSession(AD_SENDER, MASTER_KEY, NONCE)
        streams = alice.send([PLAINTEXT_1])
        received = bob.receive(streams)
        status = received[0]["status"]
        msg    = received[0]["message"]

        result("Отправлено", PLAINTEXT_1)
        result("Принято",    msg)
        result("Статус MAC", status)

        if status == "OK" and msg == PLAINTEXT_1:
            ok("Базовый раунд Alice→Bob работает корректно")
            return True
        else:
            err("Базовый раунд провалился — проверь параметры")
            return False
    except Exception as ex:
        err(f"Исключение: {ex}")
        return False

# ===========================================================================
#  АТАКА 1 (CPA): Нарушение конфиденциальности в режиме ВА
#  Обоснование: в режиме ВА (onlymac=1) сообщение передаётся ОТКРЫТЫМ
#  текстом — шифрование не применяется. Атакующий, наблюдающий канал,
#  видит plaintext напрямую. Это классическая CPA-пассивная атака.
# ===========================================================================

def attack1_VA_plaintext_exposure():
    banner("АТАКА 1 (CPA): Открытый текст в режиме ВА — нарушение конфиденциальности")

    section("Сценарий")
    info("Алиса использует режим ВА (только аутентификация, без шифрования).")
    info("Атакующий Eve перехватывает битовый поток из канала.")
    info("Вопрос: может ли Eve восстановить открытое сообщение?")

    if not IMPORTS_OK:
        section("Статический анализ (без запуска)")
        info("В EAX_CFB_frw при onlymac=1:")
        info("  MSG = MSG_IN   ← сообщение не шифруется!")
        info("  MAC = textor(textor(mac_cfb, CIV), CMAC_IN)")
        info("  Пакет: [data, IV, MSG_ОТКРЫТЫЙ, MAC]")
        info("Функция transmit() сериализует пакет в биты, затем bin2msg().")
        info("Позиция сообщения в потоке фиксирована: байты 48..48+L.")
        err("АТАКА УСПЕШНА: конфиденциальность режима ВА отсутствует по дизайну.")
        return

    section("Эксперимент")
    alice = EAXSession(AD_AUTH_ONLY, MASTER_KEY, NONCE)

    secret_msg = PLAINTEXT_2
    streams = alice.send([secret_msg])
    raw_stream = streams[0]

    # Eve перехватывает поток и разбирает его
    pkt = recieve(raw_stream)
    intercepted_msg = pkt[2]           # поле message — уже открытый текст
    intercepted_msg_unpad = unpad_message(intercepted_msg)

    section("Результат")
    result("Оригинал (Алиса)",     secret_msg)
    result("Перехвачено (Eve)",    intercepted_msg_unpad)
    result("Совпадение",           secret_msg == intercepted_msg_unpad)

    if secret_msg == intercepted_msg_unpad:
        err("АТАКА УСПЕШНА! Eve восстановила сообщение без ключа.")
        info("Уязвимость: режим ВА не обеспечивает конфиденциальность.")
        info("Рекомендация: для секретных сообщений всегда использовать ВБ.")
    else:
        ok("Сообщение не совпало — возможна ошибка в эксперименте.")

# ===========================================================================
#  АТАКА 2 (CCA): Битфлиппинг в CFB — нарушение целостности
#  Обоснование: в режиме CFB изменение i-го блока шифртекста приводит к
#  XOR-изменению i-го блока открытого текста (предсказуемое искажение)
#  и случайному уничтожению блока (i+1). Если MAC не проверяется или
#  MAC вычисляется ДО модификации атакующим, изменение проходит.
#  В режиме В_ MAC отсутствует вообще — атака тривиальна.
# ===========================================================================

def attack2_bitflip_open_channel():
    banner("АТАКА 2 (CCA): Битфлиппинг в открытом канале В_ — нарушение целостности")

    section("Сценарий")
    info("Алиса отправляет команду по открытому каналу В_.")
    info("Атакующий Eve перехватывает поток, изменяет биты и пересылает Бобу.")
    info("Цель: изменить первое слово сообщения предсказуемым образом.")
    info("В режиме В_ нет ни шифрования, ни MAC — защита отсутствует полностью.")

    if not IMPORTS_OK:
        section("Статический анализ (без запуска)")
        info("transmit() → msg2bin(header + iv + msg + mac)")
        info("Заголовок: 32 символа = 160 бит")
        info("IV: 16 символов = 80 бит")
        info("Итого смещение до msg: 240 бит")
        info("textor(A,B) = побайтовый XOR блоков по 4 символа")
        info("Замена символа в нужной позиции потока → замена символа в plaintext")
        err("АТАКА УСПЕШНА: в В_ целостность не защищена.")
        return

    section("Эксперимент")
    alice = EAXSession(AD_OPEN, MASTER_KEY, NONCE)
    bob   = EAXSession(AD_OPEN, MASTER_KEY, NONCE)

    original_msg = "АТАКА_ПРОВАЛИЛАСЬ"
    streams = alice.send([original_msg])
    stream  = list(streams[0])          # копия потока

    # Разбираем структуру пакета, чтобы найти смещение сообщения
    pkt_before = recieve(list(stream))
    msg_field_before = pkt_before[2]

    # Узнаём смещение msg в bin-потоке
    # header = type(2)+sender(8)+receiver(8)+session(9)+length(5) = 32 символа = 160 бит
    # iv = 16 символов = 80 бит  → итого 240 бит до msg
    MSG_BIT_OFFSET = 240

    result("Исходный msg field", msg_field_before)

    # Целевая замена: хотим чтобы первый символ msg стал другим
    # В В_: поток = открытый текст → просто меняем биты напрямую
    # Первый символ msg → биты [240..244]
    # Прочитаем текущие биты первого символа
    original_bits = stream[MSG_BIT_OFFSET: MSG_BIT_OFFSET + 5]
    original_char_num = 0
    for b in original_bits:
        original_char_num = 2 * original_char_num + b

    # Выберем целевой символ: 'З' (нарушение)
    target_char = 'З'
    target_num  = sym2num(target_char)

    # Вычислим XOR-маску и применим побитово
    xor_mask = original_char_num ^ target_num
    for bit_idx in range(4, -1, -1):
        flip = (xor_mask >> (4 - bit_idx)) & 1
        if flip:
            stream[MSG_BIT_OFFSET + bit_idx] ^= 1

    # Боб принимает модифицированный поток
    pkt_after = recieve(stream)
    msg_after = pkt_after[2]
    received = bob.receive([stream])

    section("Результат")
    result("Оригинал (Алиса)",        original_msg)
    result("Перехвачено до flip",      msg_field_before[:10] + "...")
    result("После битфлиппинга",       msg_after[:10] + "...")
    result("Статус у Боба",            received[0]["status"])
    result("Сообщение у Боба",         received[0]["message"])

    if received[0]["message"] != original_msg:
        err("АТАКА УСПЕШНА! Сообщение искажено без обнаружения.")
        info("Первый символ заменён с предсказуемым результатом.")
        info("Причина: в В_ нет MAC и нет шифрования.")
    else:
        ok("Сообщение не изменилось — возможно смещение неточное.")

# ===========================================================================
#  АТАКА 3 (CCA): Битфлиппинг в режиме ВБ — проверка стойкости MAC
#  Обоснование: CFB обладает свойством «самосинхронизации» — ошибка
#  в i-м блоке шифртекста даёт предсказуемое XOR в P[i] и случайную
#  порчу P[i+1]. Атакующий пытается изменить шифртекст так, чтобы
#  расшифрованный текст содержал нужное значение. Вопрос: детектирует
#  ли MAC подобную модификацию?
# ===========================================================================

def attack3_bitflip_VB_mac_check():
    banner("АТАКА 3 (CCA): Битфлиппинг шифртекста в режиме ВБ — проверка MAC")

    section("Сценарий")
    info("Алиса шифрует и аутентифицирует сообщение (режим ВБ).")
    info("Eve перехватывает поток и меняет один бит в зашифрованном сообщении.")
    info("Вопрос: обнаружит ли Боб модификацию через проверку MAC?")
    info("Ожидание: MAC должен сработать (EAX покрывает шифртекст через cont).")

    if not IMPORTS_OK:
        section("Статический анализ (без запуска)")
        info("В frw_CFB: cont накапливает XOR всех блоков открытого текста.")
        info("MAC = textor(textor(cont_cfb, CIV), CMAC)")
        info("При изменении шифртекста → меняется plaintext → меняется cont")
        info("→ вычисленный MAC не совпадёт с переданным.")
        info("НО: атакующий не знает ключ, поэтому не может пересчитать MAC.")
        ok("АТАКА ПРОВАЛИЛАСЬ: MAC детектирует модификацию шифртекста.")
        return

    section("Эксперимент")
    alice = EAXSession(AD_SENDER, MASTER_KEY, NONCE)
    bob   = EAXSession(AD_SENDER, MASTER_KEY, NONCE)

    secret_msg = PLAINTEXT_2
    streams = alice.send([secret_msg])
    stream  = list(streams[0])

    # Смещение до зашифрованного сообщения: 240 бит (аналогично атаке 2)
    # Переворачиваем один бит в середине шифртекста
    flip_pos = 300   # произвольный бит внутри зашифрованного сообщения
    if flip_pos < len(stream):
        stream[flip_pos] ^= 1
        info(f"Перевёрнут бит #{flip_pos} в шифртексте")
    else:
        info(f"Позиция {flip_pos} вне потока ({len(stream)} бит), флип пропущен")

    received = bob.receive([stream])

    section("Результат")
    result("Оригинал (Алиса)",  secret_msg)
    result("Статус у Боба",     received[0]["status"])
    result("Сообщение у Боба",  received[0]["message"])

    if received[0]["status"] == "MAC_ERROR":
        ok("АТАКА ПРОВАЛИЛАСЬ: MAC обнаружил модификацию шифртекста.")
        ok("Целостность защищена в режиме ВБ.")
        info("EAX-MAC покрывает всё зашифрованное тело — подмена детектируется.")
    elif received[0]["status"] == "OK" and received[0]["message"] != secret_msg:
        err("АТАКА ЧАСТИЧНО УСПЕШНА: сообщение изменено, MAC не сработал!")
        err("Критическая уязвимость: MAC не покрывает шифртекст должным образом.")
    else:
        info(f"Неожиданный результат: {received[0]}")

# ===========================================================================
#  АТАКА 4 (CCA): Атака с выбором IV — нарушение конфиденциальности и
#  целостности при снятии ограничения на выбор атакующим значения IV
#
#  Обоснование: в CFB-режиме если атакующий знает P[1] (первый блок
#  открытого текста) и может задать IV, то:
#    C[1] = P[1] XOR Feistel(IV)
#    P'[1] = C[1] XOR Feistel(IV') = P[1] XOR Feistel(IV) XOR Feistel(IV')
#  Выбирая IV' = IV → P'[1] = P[1] (без изменений).
#  Но выбирая IV' такой, что Feistel(IV') известен → можно подменить P'[1].
#
#  Более мощный сценарий (chosen-IV, известный plaintext):
#  Если атакующий знает P[1] и C[1] (из перехвата), то:
#    Feistel(IV) = P[1] XOR C[1]
#  Зная Feistel(IV), можно создать C'[1] = P_target XOR Feistel(IV)
#  → расшифрует в P_target. При этом MAC не пересчитан → детектируется в ВБ,
#  НО в ВА сообщение открыто, а MAC вычисляется над открытым текстом.
#
#  КЛЮЧЕВОЙ СЦЕНАРИЙ: атакующий контролирует IV в режиме ВА.
#  Он создаёт поддельный пакет с нужным сообщением и правильным MAC.
# ===========================================================================

def attack4_chosen_iv():
    banner("АТАКА 4 (Chosen-IV + CCA): Свободный выбор IV — нарушение конфиденциальности и целостности")

    section("Теоретическое обоснование")
    info("Предположение: атакующий Eve может выбирать IV при отправке пакета.")
    info("Протокол генерирует IV = IVO(12) + counter(4).")
    info("Если атакующий обходит счётчик и задаёт произвольный IV:")
    info("  В режиме ВА: MAC вычисляется над открытым plaintext.")
    info("  Зная ключи или имея CPA-оракул, Eve строит пакет с нужным MAC.")
    info("  Проще: если IV повторяется (IV reuse), то keystream повторяется.")
    info("  Два сообщения с одним IV: C1 XOR C2 = P1 XOR P2 (раскрытие текста).")

    section("Сценарий A: IV-reuse (повтор IV) — утечка XOR открытых текстов")
    info("Eve заставляет Алису дважды использовать один и тот же IV.")
    info("Это возможно, если атакующий сбрасывает счётчик сессии (replay/reset).")

    if not IMPORTS_OK:
        section("Статический анализ (без запуска)")
        info("EAXSession._next_iv() использует self.msg_counter (инкремент).")
        info("Нет защиты от replay: отдельный экземпляр EAXSession с тем же")
        info("MASTER_KEY и NONCE → счётчик начинается с -1 заново.")
        info("Атака: создать второй сеанс с теми же параметрами → IV совпадут.")
        info("P1 XOR P2 = C1 XOR C2 → зная P1, восстанавливаем P2.")
        err("АТАКА УСПЕШНА при повторе IV: XOR-утечка открытых текстов.")

        section("Сценарий B: Подделка пакета в ВА при выбранном IV")
        info("В ВА MAC = textor(textor(cfb_mac(plaintext), CIV), CMAC)")
        info("Если IV задан атакующим, CIV = frw_CFB(sec_tmp, IV_chosen, keyset, -1)")
        info("Атакующий не знает keyset → не может вычислить CIV напрямую.")
        info("Однако: если атакующий имеет CPA-оракул (может запросить шифрование")
        info("произвольного сообщения) → он получает пары (msg, mac) → строит")
        info("поддельный MAC для нового сообщения через линейные свойства XOR.")
        err("АТАКА ПОТЕНЦИАЛЬНО УСПЕШНА при CPA-оракуле + выбранном IV.")
        return

    section("Эксперимент A: IV-reuse через пересоздание сессии")

    # Алиса шифрует P1 (счётчик = 0)
    alice1 = EAXSession(AD_SENDER, MASTER_KEY, NONCE)
    streams1 = alice1.send([PLAINTEXT_1])
    C1_stream = streams1[0]

    # Eve создаёт новую сессию с теми же параметрами → счётчик сброшен в 0
    # → IV будет тем же самым!
    alice2 = EAXSession(AD_SENDER, MASTER_KEY, NONCE)
    streams2 = alice2.send([PLAINTEXT_2])
    C2_stream = streams2[0]

    # Проверяем совпадение IV
    pkt1 = recieve(list(C1_stream))
    pkt2 = recieve(list(C2_stream))
    iv1  = pkt1[1]
    iv2  = pkt2[1]
    msg1_enc = pkt1[2]   # зашифрованный текст первого сообщения
    msg2_enc = pkt2[2]   # зашифрованный текст второго сообщения

    result("IV первого сеанса",  iv1)
    result("IV второго сеанса",  iv2)
    result("IV совпадают?",      iv1 == iv2)

    if iv1 == iv2:
        err("IV СОВПАДАЮТ! Атака IV-reuse возможна.")

        # XOR шифртекстов = XOR открытых текстов (свойство потокового шифра / CFB)
        xor_result = textor(msg1_enc, msg2_enc)

        # Если Eve знает PLAINTEXT_1 (known-plaintext), она восстанавливает P2
        # P2 = P1 XOR (C1 XOR C2)
        recovered_p2 = textor(PLAINTEXT_1 + "_" * max(0, len(xor_result) - len(PLAINTEXT_1)),
                               xor_result)
        recovered_p2_trimmed = recovered_p2[:len(PLAINTEXT_2)]

        section("Known-Plaintext Recovery при IV-reuse")
        result("P1 (известен Eve)",        PLAINTEXT_1)
        result("C1 XOR C2 (перехвачено)", xor_result[:20] + "...")
        result("Восстановленный P2",       recovered_p2_trimmed)
        result("Настоящий P2",             PLAINTEXT_2)

        # Точное восстановление зависит от длин; проверяем первые символы
        match_len = min(len(recovered_p2_trimmed), len(PLAINTEXT_2))
        matches = sum(1 for a, b in zip(recovered_p2_trimmed, PLAINTEXT_2) if a == b)
        result("Совпадений символов",      f"{matches}/{match_len}")

        if matches > match_len // 2:
            err(f"АТАКА УСПЕШНА: восстановлено {matches}/{match_len} символов P2!")
        else:
            info("Частичное восстановление — точность зависит от выравнивания блоков.")
    else:
        ok("IV не совпадают — IV-reuse не сработал в данной конфигурации.")

    section("Эксперимент B: Подделка целостности в ВА при выбранном IV")
    info("Eve хочет, чтобы Боб принял сообщение 'ПОДДЕЛКА' как аутентичное.")
    info("Используем CPA-оракул: Eve запрашивает MAC для 'ПОДДЕЛКА' у Алисы,")
    info("перехватывает пакет и пересылает Бобу от своего имени.")

    # Алиса (как оракул) подписывает сообщение Eve
    alice_oracle = EAXSession(AD_AUTH_ONLY, MASTER_KEY, NONCE)
    bob_va       = EAXSession(AD_AUTH_ONLY, MASTER_KEY, NONCE)

    forged_msg = "ПОДДЕЛКА"
    oracle_streams = alice_oracle.send([forged_msg])

    # Eve пересылает поток Бобу БЕЗ изменений (replay attack)
    received = bob_va.receive(oracle_streams)

    section("Результат атаки B (replay в ВА)")
    result("Поддельное сообщение", forged_msg)
    result("Статус у Боба",        received[0]["status"])
    result("Принятое сообщение",   received[0]["message"])

    if received[0]["status"] == "OK" and received[0]["message"] == forged_msg:
        err("REPLAY АТАКА УСПЕШНА! Боб принял поддельное сообщение как аутентичное.")
        info("Причина: нет защиты от повтора (replay protection) — счётчик не проверяется получателем.")
        info("Рекомендация: получатель должен отслеживать принятые счётчики/nonce.")
    else:
        ok(f"Атака не прошла: статус={received[0]['status']}")

# ===========================================================================
#  АТАКА 5 (CCA): Replay attack — нарушение свежести сообщений
#  Обоснование: протокол не проверяет счётчик на стороне получателя.
#  Атакующий перехватывает легитимный пакет и отправляет его повторно.
# ===========================================================================

def attack5_replay():
    banner("АТАКА 5 (CCA): Атака повтора (Replay Attack) — нарушение свежести")

    section("Сценарий")
    info("Алиса отправляет команду 'ОТКРЫТЬ' в режиме ВБ (шифрование + MAC).")
    info("Eve перехватывает пакет и воспроизводит его позже повторно.")
    info("Вопрос: примет ли Боб повторный пакет как легитимный?")

    if not IMPORTS_OK:
        section("Статический анализ (без запуска)")
        info("EAXSession.receive() не хранит историю принятых IV/счётчиков.")
        info("Каждый пакет проверяется независимо по MAC.")
        info("Повторный пакет имеет корректный MAC → будет принят.")
        err("АТАКА УСПЕШНА: replay protection отсутствует.")
        return

    section("Эксперимент")
    alice = EAXSession(AD_SENDER, MASTER_KEY, NONCE)
    bob   = EAXSession(AD_SENDER, MASTER_KEY, NONCE)

    cmd = "ОТКРЫТЬ"
    streams = alice.send([cmd])
    original_stream = streams[0]

    # Боб принимает первый раз
    result1 = bob.receive([list(original_stream)])
    # Eve воспроизводит тот же поток
    result2 = bob.receive([list(original_stream)])

    section("Результат")
    result("Команда Алисы",              cmd)
    result("Первое получение (статус)",  result1[0]["status"])
    result("Первое получение (msg)",     result1[0]["message"])
    result("Повтор Eve (статус)",        result2[0]["status"])
    result("Повтор Eve (msg)",           result2[0]["message"])

    if result2[0]["status"] == "OK" and result2[0]["message"] == cmd:
        err("АТАКА УСПЕШНА! Боб принял повторный пакет без ошибки.")
        err("Нарушение свежести: команда выполнена дважды.")
        info("Уязвимость: отсутствие окна принятия / списка использованных nonce.")
        info("Рекомендация: хранить принятые счётчики; отклонять дубликаты.")
    else:
        ok("Повторный пакет отклонён — replay protection работает.")

# ===========================================================================
#  ИТОГОВЫЙ ОТЧЁТ
# ===========================================================================

def print_summary(results: dict):
    banner("ИТОГОВЫЙ ОТЧЁТ ПЕНТЕСТИНГА")

    table = [
        ("Атака 0", "Sanity check среды",                       "—"),
        ("Атака 1", "CPA: открытый текст в режиме ВА",           "ДА (по дизайну)"),
        ("Атака 2", "CCA: битфлиппинг в В_ (нет MAC)",           "ДА"),
        ("Атака 3", "CCA: битфлиппинг в ВБ (проверка MAC)",      "НЕТ (MAC работает)"),
        ("Атака 4", "Chosen-IV: IV-reuse + replay в ВА",         "ЧАСТИЧНО"),
        ("Атака 5", "CCA: replay attack (нет счётчика у Боба)",  "ДА"),
    ]

    print(f"\n  {'Атака':<10} {'Описание':<45} {'Успех'}")
    print(f"  {'-'*10} {'-'*45} {'-'*20}")
    for row in table:
        print(f"  {row[0]:<10} {row[1]:<45} {row[2]}")

    print(f"""
{SEP2}
  ВЫВОДЫ:

  1. Режим В_ (открытый канал) не обеспечивает ни конфиденциальности,
     ни целостности. Любой атакующий может читать и изменять сообщения.

  2. Режим ВА (только MAC) не обеспечивает конфиденциальности:
     сообщения передаются открытым текстом. При наличии CPA-оракула
     атакующий может получить корректный MAC для произвольного сообщения.

  3. Режим ВБ (шифрование + MAC, EAX) устойчив к битфлиппингу:
     MAC детектирует любое изменение шифртекста.

  4. Уязвимость IV-reuse: при повторном использовании IV (например,
     сброс сессии) шифрование CFB вырождается в XOR с повторяющимся
     ключевым потоком. При known-plaintext атакующий восстанавливает
     второй открытый текст через P2 = P1 XOR C1 XOR C2.

  5. Отсутствие replay protection: получатель не отслеживает
     использованные счётчики/nonce. Легитимный перехваченный пакет
     принимается повторно с корректным MAC.

  РЕКОМЕНДАЦИИ:
  - Использовать только режим ВБ для секретных данных.
  - Реализовать на стороне получателя окно принятия или
    журнал использованных nonce/счётчиков.
  - Никогда не допускать IV-reuse (привязать nonce к монотонному
    глобальному счётчику, сохраняемому между сессиями).
{SEP2}
""")

# ===========================================================================
#  ТОЧКА ВХОДА
# ===========================================================================

if __name__ == "__main__":
    print(SEP)
    print("  ПЕНТЕСТИНГ ПРОТОКОЛА EAX-CFB")
    print("  Атаки: CPA, CCA, Chosen-IV, Replay")
    if IMPORTS_OK:
        print("  Режим: LIVE (импорты успешны)")
    else:
        print("  Режим: СТАТИЧЕСКИЙ АНАЛИЗ (импорты не найдены)")
        print(f"  Причина: {_IMPORT_ERROR}")
    print(SEP)

    results = {}

    results["sanity"]   = attack0_sanity()
    attack1_VA_plaintext_exposure()
    attack2_bitflip_open_channel()
    attack3_bitflip_VB_mac_check()
    attack4_chosen_iv()
    attack5_replay()
    print_summary(results)