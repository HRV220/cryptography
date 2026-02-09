from Alphabet import TelegraphAlphabet
from TritimiusCipher import TrithemiusCipher

if __name__ == "__main__":
    alphabet = TelegraphAlphabet()

    # 1. Простой шифр Тритемуса (одиночный символ)
    print("1. Простой шифр Тритемуса (одиночный символ):")
    print("-" * 60)
    symbol = "Г"
    keys = ["ЧЕРНОСОТЕНЦЫ", "АБВГД", "ХОРОШО_БЫТЬ_ВАМИ"]

    for key in keys:
        work = alphabet.build_alphabet(key)
        enc = TrithemiusCipher.encrypt_char(symbol, work)
        dec = TrithemiusCipher.decrypt_char(enc, work)
        print(f"  K='{key}':  '{symbol}' -> '{enc}' -> '{dec}'")

    # 2. Простой шифр Тритемуса (блок текста)
    print(f"\n2. Простой шифр Тритемуса (блок текста):")
    print("-" * 60)
    text = "ГОЛОВНОЙ_ОФИС"

    for key in keys:
        work = alphabet.build_alphabet(key)
        enc = TrithemiusCipher.encrypt(text, work)
        dec = TrithemiusCipher.decrypt(enc, work)
        print(f"  K='{key}':")
        print(f"    {text} -> {enc} -> {dec}")

    # 3. Полиалфавитный шифр Тритемуса
    print(f"\n3. Полиалфавитный шифр Тритемуса:")
    print("-" * 60)

    K1 = "АББАТ_ТРИТИМУС"
    K2 = "БАБАТ_ТРИТИМУС"
    K3 = "ТРИТИМУС_АББАТ"
    IN1 = "ОТКРЫТЫЙ_ТЕКСТ"
    IN2 = "ДЛИННЫЙ_ОТКРЫТЫЙ_ТЕКСТ"

    # Шифрование
    OUT0 = TrithemiusCipher.encrypt_poly(IN1, K1)
    OUT1 = TrithemiusCipher.encrypt_poly(IN1, K2)
    OUT3 = TrithemiusCipher.encrypt_poly(IN2, K1)
    OUT4 = TrithemiusCipher.encrypt_poly(IN2, K3)

    print(f"  encrypt_poly('{IN1}', K1) = {OUT0}")
    print(f"  encrypt_poly('{IN1}', K2) = {OUT1}")
    print(f"  OUT0 == OUT1: {OUT0 == OUT1}")
    print()
    print(f"  encrypt_poly('{IN2}', K1) = {OUT3}")
    print(f"  encrypt_poly('{IN2}', K3) = {OUT4}")

    # Расшифрование
    print(f"\n  Расшифрование:")
    print(f"  decrypt_poly(OUT0, K1) = {TrithemiusCipher.decrypt_poly(OUT0, K1)}")
    print(f"  decrypt_poly(OUT1, K2) = {TrithemiusCipher.decrypt_poly(OUT1, K2)}")
    print(f"  decrypt_poly(OUT1, K1) = {TrithemiusCipher.decrypt_poly(OUT1, K1)}")
    print(f"  decrypt_poly(OUT4, K3) = {TrithemiusCipher.decrypt_poly(OUT4, K3)}")

    # 4. S-блок (P=4 символа, K=16 символов)
    print(f"\n4. S-блок (блок 4 символа, ключ 16 символов):")
    print("-" * 60)

    key16 = "АББАТ_ТРИТИМУСЫЫ"  # 16 символов
    blocks = ["АБВГ", "АБВД", "ГВБА", "ЯЯЯЯ"]

    for block in blocks:
        enc = TrithemiusCipher.s_block_encrypt(block, key16)
        dec = TrithemiusCipher.s_block_decrypt(enc, key16)
        print(f"  S('{block}', K) = '{enc}'  |  S⁻¹('{enc}', K) = '{dec}'")

    # 5. Усиленный S-блок (mix -> encrypt -> mix)
    print(f"\n5. Усиленный S-блок (strong):")
    print("-" * 60)

    for block in blocks:
        enc = TrithemiusCipher.s_block_encrypt_strong(block, key16)
        dec = TrithemiusCipher.s_block_decrypt_strong(enc, key16)
        print(f"  S_strong('{block}', K) = '{enc}'  |  S⁻¹_strong('{enc}', K) = '{dec}'")

    # 6. Сравнение: малое изменение входа
    print(f"\n6. Чувствительность к малому изменению входа:")
    print("-" * 60)
    p1, p2 = "АБВГ", "АБВД"
    c1 = TrithemiusCipher.s_block_encrypt(p1, key16)
    c2 = TrithemiusCipher.s_block_encrypt(p2, key16)
    c1s = TrithemiusCipher.s_block_encrypt_strong(p1, key16)
    c2s = TrithemiusCipher.s_block_encrypt_strong(p2, key16)
    diff = sum(1 for a, b in zip(c1, c2) if a != b)
    diff_s = sum(1 for a, b in zip(c1s, c2s) if a != b)
    print(f"  P='{p1}' vs P'='{p2}'")
    print(f"  Без усиления:  S(P)='{c1}', S(P')='{c2}' — различий: {diff}/4")
    print(f"  С усилением:   S(P)='{c1s}', S(P')='{c2s}' — различий: {diff_s}/4")
