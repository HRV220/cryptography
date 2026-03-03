# -*- coding: utf-8 -*-
"""
Демонстрация ЛР2: ядро односторонней функции, C-блок и хеш (Merkle–Damgård).
Структура файла аналогична lab1/main.py — последовательные секции с выводом.
"""

from c_block import (
    core_trithemius,
    CBlock,
    MerDam_hash,
    confuse,
)


def diff_count(a: str, b: str) -> int:
    """Количество позиций, в которых строки отличаются (по минимальной длине)."""
    m = min(len(a), len(b))
    return sum(1 for i in range(m) if a[i] != b[i])


if __name__ == "__main__":
    print("1. Ядро односторонней функции (на основе Тритимуса):")
    print("-" * 60)
    IN1 = "ХОРОШО_БЫТЬ_ВАМИ"  # 16
    IN2 = "КЬЕРКЕГОР_ПРОПАЛ"  # 16
    OUT12 = core_trithemius(IN1, IN2)
    OUT21 = core_trithemius(IN2, IN1)
    print(f"  core_trithemius(IN1, IN2) = {OUT12}")
    print(f"  core_trithemius(IN2, IN1) = {OUT21}")

    print(f"\n2. C-блок (вход: последовательность по 16 символов; выход: 16/8/4):")
    print("-" * 60)
    cb = CBlock()
    blocks = [IN1, IN2]
    out16 = cb.c_block(blocks, 16)
    out08 = cb.c_block(blocks, 8)
    out04 = cb.c_block(blocks, 4)
    print(f"  C_block([{', '.join(blocks)}], 16) = {out16}")
    print(f"  C_block([{', '.join(blocks)}],  8) = {out08}")
    print(f"  C_block([{', '.join(blocks)}],  4) = {out04}")

    print(f"\n3. Чувствительность C-блока к малому изменению входа:")
    print("-" * 60)
    P = "АБВГДЕЖЗИЙКЛМНОП"    # 16
    Pp = "АБВГДЕЖЗИЙКЛМНОР"   # отличается на последний символ
    oP = cb.c_block([P], 16)
    oPp = cb.c_block([Pp], 16)
    d = diff_count(oP, oPp)
    print(f"  P   = {P}")
    print(f"  P'  = {Pp}")
    print(f"  C(P)  = {oP}")
    print(f"  C(P') = {oPp}")
    print(f"  Различий в выходе: {d}/16 (демонстрация возможной низкой чувствительности)")

    IN  = "ХОРОШО_БЫТЬ_ВАМИ"
    IN1 = "КЬЕРКЕГОР_ПРОПАЛ"
    IN2 = "ХОРОШО_ПРОБРОСИЛ"

    print(f"\n4. Хеш-функция Merkle–Damgard на базе C-блока и ядра:")
    print("-" * 60)
    messages = [
        "",                       # пустая строка
        "_",                      # один символ
        IN1 + IN2,                # 32 символа
        "ПРИВЕТ_МИР",             # короче 64
        "ПЕТЯ_ПИЛ_ПИВО_В_КАЛЬЯННОЙ_И_КУРИЛ_БАМБУК_ЧЕРЕЗ_АНАНАС_ТЧК_НАСТЯ_ПИЛА_ВОДУ_И_НЕ_ПОШЛА_В_КАЛЬЯННУЮ_ЗПТ_ЧТОБЫ_ВЫСПАТЬСЯ",
    ]
    for msg in messages:
        h = MerDam_hash(msg)
        short = (msg[:20] + '...') if len(msg) > 20 else msg
        print(f"  MerDam_hash('{short}') = {h}")
