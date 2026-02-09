from Alphabet import TelegraphAlphabet, TelegraphChar


class TrithemiusCipher:
    """Шифр Тритемуса (простая замена со сдвигом на 8 в рабочем алфавите)"""

    SHIFT = 8

    @staticmethod
    def shift_table(table: TelegraphAlphabet, sym_in: str, bias_in: int) -> TelegraphAlphabet:
        """
        Сдвиг ключевой таблицы для шифра Тритемуса.

        Алгоритм:
        1. Разделить таблицу на rem (первые bias_in символов) и str (остальные).
        2. Взять sym_in; если он уже в rem — сдвигать до свободного.
        3. Убрать найденный символ из str.
        4. Новая таблица = [s] + rem + str (без s).

        Args:
            table: Текущая рабочая таблица
            sym_in: Символ для сдвига
            bias_in: Смещение (размер «головы»)

        Returns:
            Новая TelegraphAlphabet после сдвига
        """
        std = TelegraphAlphabet()

        s = sym_in
        rem = [ch.char for ch in table[0:bias_in]]
        str_part = [ch.char for ch in table[bias_in:32]]

        # Если s уже есть в rem — сдвигаем до свободного
        while s in rem:
            s = std[(std[s].value + 1) % 32].char

        # Убираем s из str_part
        str_part.remove(s)

        # TABLE_OUT = [s] + rem + str_part
        new_order = [s] + rem + str_part
        new_symbols = {char: idx for idx, char in enumerate(new_order)}

        return TelegraphAlphabet(new_symbols)

    @staticmethod
    def encrypt_char(char: str, work_alphabet: TelegraphAlphabet) -> str:
        """
        Зашифрование одного символа.
        Сдвиг на +8 позиций в рабочем алфавите.

        Args:
            char: Символ открытого текста
            work_alphabet: Рабочий алфавит

        Returns:
            Символ шифротекста
        """
        value = work_alphabet.get_value_by_char(char.upper())
        new_value = (value + TrithemiusCipher.SHIFT) % 32
        return work_alphabet.get_char_by_value(new_value).char

    @staticmethod
    def decrypt_char(char: str, work_alphabet: TelegraphAlphabet) -> str:
        """
        Расшифрование одного символа.
        Сдвиг на -8 позиций в рабочем алфавите.

        Args:
            char: Символ шифротекста
            work_alphabet: Рабочий алфавит

        Returns:
            Символ открытого текста
        """
        value = work_alphabet.get_value_by_char(char.upper())
        new_value = (value - TrithemiusCipher.SHIFT + 32) % 32
        return work_alphabet.get_char_by_value(new_value).char

    @staticmethod
    def encrypt(plaintext: str, work_alphabet: TelegraphAlphabet) -> str:
        """
        Зашифрование блока текста (простой шифр Тритемуса).
        Применяет encrypt_char последовательно к каждому символу.
        """
        return ''.join(
            TrithemiusCipher.encrypt_char(ch, work_alphabet)
            for ch in plaintext.upper()
        )

    @staticmethod
    def decrypt(ciphertext: str, work_alphabet: TelegraphAlphabet) -> str:
        """
        Расшифрование блока текста (простой шифр Тритемуса).
        Применяет decrypt_char последовательно к каждому символу.
        """
        return ''.join(
            TrithemiusCipher.decrypt_char(ch, work_alphabet)
            for ch in ciphertext.upper()
        )

    @staticmethod
    def encrypt_poly(plaintext: str, key: str, alphabet: TelegraphAlphabet = None) -> str:
        """
        Полиалфавитное зашифрование текста (шифр Тритемуса).

        После каждого символа ключевая таблица сдвигается через shift_table,
        что делает шифр полиалфавитным.

        Args:
            plaintext: Открытый текст
            key: Ключевая фраза
            alphabet: Исходный алфавит (по умолчанию стандартный)

        Returns:
            Шифротекст
        """
        if alphabet is None:
            alphabet = TelegraphAlphabet()
        std = TelegraphAlphabet()

        key_upper = key.upper()
        key_table = alphabet.build_alphabet(key_upper)
        key_len = len(key_upper)

        out = []
        for i, ch in enumerate(plaintext.upper()):
            k = i % key_len
            b = (key_len + i) % 32

            csym = TrithemiusCipher.encrypt_char(ch, key_table)
            key_table = TrithemiusCipher.shift_table(key_table, std[std[key_upper[k]].value].char, b)
            out.append(csym)

        return ''.join(out)

    @staticmethod
    def decrypt_poly(ciphertext: str, key: str, alphabet: TelegraphAlphabet = None) -> str:
        """
        Полиалфавитное расшифрование текста (шифр Тритемуса).

        Args:
            ciphertext: Шифротекст
            key: Ключевая фраза
            alphabet: Исходный алфавит (по умолчанию стандартный)

        Returns:
            Открытый текст
        """
        if alphabet is None:
            alphabet = TelegraphAlphabet()
        std = TelegraphAlphabet()

        key_upper = key.upper()
        key_table = alphabet.build_alphabet(key_upper)
        key_len = len(key_upper)

        out = []
        for i, ch in enumerate(ciphertext.upper()):
            k = i % key_len
            b = (key_len + i) % 32

            csym = TrithemiusCipher.decrypt_char(ch, key_table)
            key_table = TrithemiusCipher.shift_table(key_table, std[std[key_upper[k]].value].char, b)
            out.append(csym)

        return ''.join(out)

    # --- S-блок (блочное шифрование по 4 символа, ключ 16 символов) ---

    BLOCK_SIZE = 4
    KEY_SIZE = 16

    @staticmethod
    def s_block_encrypt(block: str, key: str, alphabet: TelegraphAlphabet = None) -> str:
        """
        S-блок: зашифрование блока из 4 символов ключом из 16 символов.
        Использует полиалфавитный шифр Тритемуса.

        Args:
            block: Открытый текст (ровно 4 символа)
            key: Ключ (ровно 16 символов)
            alphabet: Исходный алфавит (по умолчанию стандартный)

        Returns:
            Шифротекст (4 символа)
        """
        if len(block) != TrithemiusCipher.BLOCK_SIZE:
            raise ValueError(f"Блок должен быть {TrithemiusCipher.BLOCK_SIZE} символа, получено {len(block)}")
        if len(key) != TrithemiusCipher.KEY_SIZE:
            raise ValueError(f"Ключ должен быть {TrithemiusCipher.KEY_SIZE} символов, получено {len(key)}")

        return TrithemiusCipher.encrypt_poly(block, key, alphabet)

    @staticmethod
    def s_block_decrypt(block: str, key: str, alphabet: TelegraphAlphabet = None) -> str:
        """
        S-блок: расшифрование блока из 4 символов ключом из 16 символов.

        Args:
            block: Шифротекст (ровно 4 символа)
            key: Ключ (ровно 16 символов)
            alphabet: Исходный алфавит (по умолчанию стандартный)

        Returns:
            Открытый текст (4 символа)
        """
        if len(block) != TrithemiusCipher.BLOCK_SIZE:
            raise ValueError(f"Блок должен быть {TrithemiusCipher.BLOCK_SIZE} символа, получено {len(block)}")
        if len(key) != TrithemiusCipher.KEY_SIZE:
            raise ValueError(f"Ключ должен быть {TrithemiusCipher.KEY_SIZE} символов, получено {len(key)}")

        return TrithemiusCipher.decrypt_poly(block, key, alphabet)

    # --- Усиление S-блока (перемешивание символов) ---

    @staticmethod
    def _get_mixing_order(key: str, alphabet: TelegraphAlphabet = None) -> list:
        """
        Вычисление порядка перемешивания на основе ключа.

        q = n(K1) - n(K2) + n(K3) - ... - n(K16)
        Из q извлекаем q1, q2, q3 (факториальная система счисления),
        которые определяют перестановку индексов [q1, q2, q3, q4].

        Returns:
            Список из 4 индексов — порядок перемешивания
        """
        if alphabet is None:
            alphabet = TelegraphAlphabet()

        # q = n(K1) - n(K2) + n(K3) - ... - n(K16)
        q = 0
        for i, ch in enumerate(key.upper()):
            val = alphabet[ch].value
            if i % 2 == 0:
                q += val
            else:
                q -= val
        q = abs(q)

        # Факториальная система: перестановка из 4 элементов
        available = [0, 1, 2, 3]
        perm = []
        perm.append(available.pop(q % 4)); q //= 4
        perm.append(available.pop(q % 3)); q //= 3
        perm.append(available.pop(q % 2))
        perm.append(available[0])

        return perm

    @staticmethod
    def _mix(block: str, key: str, alphabet: TelegraphAlphabet = None) -> str:
        """
        Прямое перемешивание блока (зависимое от ключа).

        E[q2] = E[q2] + E[q1]
        E[q3] = E[q3] + E[q2]
        E[q4] = E[q4] + E[q3]
        E[q1] = E[q1] + E[q4]
        """
        if alphabet is None:
            alphabet = TelegraphAlphabet()

        q1, q2, q3, q4 = TrithemiusCipher._get_mixing_order(key, alphabet)
        E = [alphabet[ch] for ch in block.upper()]

        E[q2] = E[q2] + E[q1]
        E[q3] = E[q3] + E[q2]
        E[q4] = E[q4] + E[q3]
        E[q1] = E[q1] + E[q4]

        return ''.join(ch.char for ch in E)

    @staticmethod
    def _unmix(block: str, key: str, alphabet: TelegraphAlphabet = None) -> str:
        """
        Обратное перемешивание блока (расшифрование).

        Операции в обратном порядке:
        E[q1] = E[q1] - E[q4]
        E[q4] = E[q4] - E[q3]
        E[q3] = E[q3] - E[q2]
        E[q2] = E[q2] - E[q1]
        """
        if alphabet is None:
            alphabet = TelegraphAlphabet()

        q1, q2, q3, q4 = TrithemiusCipher._get_mixing_order(key, alphabet)
        E = [alphabet[ch] for ch in block.upper()]

        E[q1] = E[q1] - E[q4]
        E[q4] = E[q4] - E[q3]
        E[q3] = E[q3] - E[q2]
        E[q2] = E[q2] - E[q1]

        return ''.join(ch.char for ch in E)

    @staticmethod
    def s_block_encrypt_strong(block: str, key: str, alphabet: TelegraphAlphabet = None) -> str:
        """
        Усиленный S-блок: mix -> encrypt -> mix.

        Перемешивание применяется дважды (до и после шифрования),
        что гарантирует изменение всех символов при изменении одного.

        Args:
            block: Открытый текст (4 символа)
            key: Ключ (16 символов)
            alphabet: Исходный алфавит

        Returns:
            Шифротекст (4 символа)
        """
        if len(block) != TrithemiusCipher.BLOCK_SIZE:
            raise ValueError(f"Блок должен быть {TrithemiusCipher.BLOCK_SIZE} символа, получено {len(block)}")
        if len(key) != TrithemiusCipher.KEY_SIZE:
            raise ValueError(f"Ключ должен быть {TrithemiusCipher.KEY_SIZE} символов, получено {len(key)}")

        mixed = TrithemiusCipher._mix(block, key, alphabet)
        encrypted = TrithemiusCipher.encrypt_poly(mixed, key, alphabet)
        result = TrithemiusCipher._mix(encrypted, key, alphabet)
        return result

    @staticmethod
    def s_block_decrypt_strong(block: str, key: str, alphabet: TelegraphAlphabet = None) -> str:
        """
        Усиленный S-блок (расшифрование): unmix -> decrypt -> unmix.

        Args:
            block: Шифротекст (4 символа)
            key: Ключ (16 символов)
            alphabet: Исходный алфавит

        Returns:
            Открытый текст (4 символа)
        """
        if len(block) != TrithemiusCipher.BLOCK_SIZE:
            raise ValueError(f"Блок должен быть {TrithemiusCipher.BLOCK_SIZE} символа, получено {len(block)}")
        if len(key) != TrithemiusCipher.KEY_SIZE:
            raise ValueError(f"Ключ должен быть {TrithemiusCipher.KEY_SIZE} символов, получено {len(key)}")

        unmixed = TrithemiusCipher._unmix(block, key, alphabet)
        decrypted = TrithemiusCipher.decrypt_poly(unmixed, key, alphabet)
        result = TrithemiusCipher._unmix(decrypted, key, alphabet)
        return result
