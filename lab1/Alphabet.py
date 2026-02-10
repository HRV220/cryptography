"""
Модуль для работы с русским телеграфным алфавитом и шифрами замены.

Содержит классы:
- TelegraphChar: Класс для представления одного символа телеграфного алфавита
- TelegraphAlphabet: Класс для представления телеграфного алфавита (коллекция символов)
"""


class TelegraphChar:
    """
    Класс для представления символа телеграфного алфавита.

    Каждый символ имеет:
    - char: строковое представление (например, 'А')
    - value: числовое значение от 0 до 31
    - binary: двоичное представление (5 бит)
    - alphabet: ссылка на алфавит, к которому принадлежит символ
    """

    def __init__(self, char: str, value: int, alphabet=None):
        """
        Инициализация символа.

        Args:
            char: Символ (строка, обычно 1 символ)
            value: Числовое значение (0-31)
            alphabet: Ссылка на объект TelegraphAlphabet
        """
        if not 0 <= value <= 31:
            raise ValueError(f"Значение должно быть от 0 до 31, получено {value}")

        self._char = char
        self._value = value
        self.alphabet = alphabet

    # --- Свойства ---

    @property
    def char(self) -> str:
        """Получить символ как строку"""
        return self._char

    @property
    def value(self) -> int:
        """Получить числовое значение (0-31)"""
        return self._value

    @property
    def binary(self) -> str:
        """Получить двоичное представление (5 бит)"""
        return format(self._value, '05b')

    # --- Арифметические операции над символами ---

    def __add__(self, other):
        """
        Сложение символов: self + other
        Формула: n(Z) = mod[n(X) + n(Y), 32]
        """
        if not isinstance(other, TelegraphChar):
            # Автоматическое приведение типа
            if self.alphabet is None:
                raise ValueError("Невозможно выполнить операцию: символ не привязан к алфавиту")
            other = self.alphabet._convert_to_char(other)

        # Проверяем совместимость алфавитов
        if self.alphabet is not None and other.alphabet is not None:
            if self.alphabet is not other.alphabet:
                raise ValueError("Символы принадлежат разным алфавитам")

        result_value = (self._value + other._value) % 32

        # Создаем новый символ в том же алфавите
        if self.alphabet is not None:
            return self.alphabet.get_char_by_value(result_value)
        else:
            return TelegraphChar(f"#{result_value}", result_value, None)

    def __sub__(self, other):
        """
        Вычитание символов: self - other
        Формула: n(Z) = mod[32 + n(X) - n(Y), 32]
        """
        if not isinstance(other, TelegraphChar):
            # Автоматическое приведение типа
            if self.alphabet is None:
                raise ValueError("Невозможно выполнить операцию: символ не привязан к алфавиту")
            other = self.alphabet._convert_to_char(other)

        # Проверяем совместимость алфавитов
        if self.alphabet is not None and other.alphabet is not None:
            if self.alphabet is not other.alphabet:
                raise ValueError("Символы принадлежат разным алфавитам")

        result_value = (32 + self._value - other._value) % 32

        # Создаем новый символ в том же алфавите
        if self.alphabet is not None:
            return self.alphabet.get_char_by_value(result_value)
        else:
            return TelegraphChar(f"#{result_value}", result_value, None)

    def __radd__(self, other):
        """Обратное сложение: other + self"""
        if not isinstance(other, TelegraphChar):
            if self.alphabet is None:
                raise ValueError("Невозможно выполнить операцию: символ не привязан к алфавиту")
            other = self.alphabet._convert_to_char(other)
        return other.__add__(self)

    def __rsub__(self, other):
        """Обратное вычитание: other - self"""
        if not isinstance(other, TelegraphChar):
            if self.alphabet is None:
                raise ValueError("Невозможно выполнить операцию: символ не привязан к алфавиту")
            other = self.alphabet._convert_to_char(other)
        return other.__sub__(self)

    # --- Операции сравнения ---

    def __eq__(self, other):
        """Проверка на равенство"""
        if not isinstance(other, TelegraphChar):
            return False
        return self._value == other._value and self._char == other._char

    def __ne__(self, other):
        """Проверка на неравенство"""
        return not self.__eq__(other)

    def __lt__(self, other):
        """Меньше (по значению)"""
        if not isinstance(other, TelegraphChar):
            if self.alphabet is None:
                raise ValueError("Невозможно сравнить: символ не привязан к алфавиту")
            other = self.alphabet._convert_to_char(other)
        return self._value < other._value

    def __le__(self, other):
        """Меньше или равно"""
        return self == other or self < other

    def __gt__(self, other):
        """Больше"""
        if not isinstance(other, TelegraphChar):
            if self.alphabet is None:
                raise ValueError("Невозможно сравнить: символ не привязан к алфавиту")
            other = self.alphabet._convert_to_char(other)
        return self._value > other._value

    def __ge__(self, other):
        """Больше или равно"""
        return self == other or self > other

    # --- Представление объекта ---

    def __repr__(self):
        """Официальное строковое представление для отладки"""
        if self.alphabet is not None:
            return f"TelegraphChar('{self._char}', {self._value}, alphabet_id={id(self.alphabet)})"
        else:
            return f"TelegraphChar('{self._char}', {self._value})"

    def __str__(self):
        """Человекочитаемое строковое представление"""
        return self._char

    def __int__(self):
        """Преобразование к целому числу"""
        return self._value

    def __index__(self):
        """Для использования в bin(), oct(), hex()"""
        return self._value

    def __hash__(self):
        """Хэш для использования в словарях и множествах"""
        return hash((self._char, self._value, id(self.alphabet) if self.alphabet else None))


class TelegraphAlphabet:
    """
    Класс для представления телеграфного алфавита.

    Телеграфный алфавит - это ФИКСИРОВАННАЯ коллекция из 32 объектов TelegraphChar,
    так как использует 5-битное кодирование (2^5 = 32).

    Каждый слот (0-31) всегда содержит ровно один символ.
    Символы можно ЗАМЕНЯТЬ, но нельзя удалять или добавлять слоты.

    Функциональность:
    - Доступ к символам по строке, значению или бинарному коду
    - Замена символов в слотах (replace_symbol, replace_symbol_by_binary)
    - Обмен символов между слотами (swap_symbols)
    - Арифметические операции над символами
    - Итерация по символам
    - Сброс к стандартным значениям (reset)
    """

    # Стандартный русский телеграфный алфавит (32 символа)
    # Символы расположены так: А-Я (коды 0-30), '_' (код 31)
    DEFAULT_SYMBOLS = {
        'А': 0,  'Б': 1,  'В': 2,  'Г': 3,
        'Д': 4,  'Е': 5,  'Ж': 6,  'З': 7,
        'И': 8,  'Й': 9,  'К': 10, 'Л': 11,
        'М': 12, 'Н': 13, 'О': 14, 'П': 15,
        'Р': 16, 'С': 17, 'Т': 18, 'У': 19,
        'Ф': 20, 'Х': 21, 'Ц': 22, 'Ч': 23,
        'Ш': 24, 'Щ': 25, 'Ы': 26, 'Ь': 27,
        'Э': 28, 'Ю': 29, 'Я': 30, '_': 31
    }

    def __init__(self, symbols=None):
        """
        Инициализация алфавита.

        Телеграфный алфавит ВСЕГДА содержит ровно 32 символа (0-31),
        так как использует 5-битное кодирование.

        Args:
            symbols: Словарь {символ: значение}. Если None, используется DEFAULT_SYMBOLS.
                     ВАЖНО: должен содержать все 32 значения от 0 до 31!
        """
        self._symbols = {}  # dict[str, TelegraphChar]
        self._codes = {}    # dict[int, TelegraphChar] - ВСЕГДА 32 элемента

        # Заполняем алфавит - ОБЯЗАТЕЛЬНО все 32 символа
        initial_symbols = symbols if symbols is not None else self.DEFAULT_SYMBOLS

        # Проверяем, что предоставлены все 32 значения
        if len(initial_symbols) != 32:
            raise ValueError(f"Телеграфный алфавит должен содержать ровно 32 символа, получено {len(initial_symbols)}")

        # Проверяем, что все значения от 0 до 31 присутствуют
        values = set(initial_symbols.values())
        if values != set(range(32)):
            missing = set(range(32)) - values
            raise ValueError(f"В алфавите отсутствуют значения: {sorted(missing)}")

        for char, value in initial_symbols.items():
            self._add_char_object(char, value)

    def _add_char_object(self, char: str, value: int):
        """
        Внутренний метод для добавления объекта TelegraphChar.

        Args:
            char: Символ
            value: Значение (0-31)
        """
        if not 0 <= value <= 31:
            raise ValueError(f"Значение должно быть от 0 до 31, получено {value}")

        # Создаем новый объект TelegraphChar
        char_obj = TelegraphChar(char, value, alphabet=self)

        # Добавляем в оба словаря
        self._symbols[char] = char_obj
        self._codes[value] = char_obj

    def _convert_to_char(self, value):
        """
        Внутренний метод для автоматического преобразования в TelegraphChar.

        Args:
            value: str (символ), int (значение) или TelegraphChar

        Returns:
            TelegraphChar
        """
        if isinstance(value, TelegraphChar):
            return value
        elif isinstance(value, str):
            if value in self._symbols:
                return self._symbols[value]
            elif len(value) == 5 and all(c in '01' for c in value):
                # Бинарная строка
                return self.get_char_by_binary(value)
            else:
                raise ValueError(f"Символ '{value}' не найден в алфавите")
        elif isinstance(value, int):
            return self.get_char_by_value(value)
        else:
            raise TypeError(f"Неподдерживаемый тип: {type(value)}")

    # --- Методы получения символов ---

    def get_char_by_value(self, value: int) -> TelegraphChar:
        """
        Получение символа по числовому значению (0-31).

        Args:
            value: Числовое значение

        Returns:
            Объект TelegraphChar
        """
        if not 0 <= value <= 31:
            raise ValueError(f"Значение должно быть от 0 до 31, получено {value}")

        # Используем маску для 5 битов
        code = value & 0b11111

        if code in self._codes:
            return self._codes[code]
        else:
            raise ValueError(f"Символ со значением {value} не найден в алфавите")

    def get_char_by_symbol(self, symbol: str) -> TelegraphChar:
        """
        Получение символа по строковому представлению.

        Args:
            symbol: Символ (строка)

        Returns:
            Объект TelegraphChar
        """
        if symbol not in self._symbols:
            raise ValueError(f"Символ '{symbol}' не найден в алфавите")

        return self._symbols[symbol]

    def get_char_by_binary(self, binary_str: str) -> TelegraphChar:
        """
        Получение символа по бинарной строке (5 бит).

        Args:
            binary_str: Бинарная строка (например, '00001')

        Returns:
            Объект TelegraphChar
        """
        if len(binary_str) != 5 or not all(c in '01' for c in binary_str):
            raise ValueError(f"Некорректная бинарная строка: '{binary_str}'. Должно быть 5 символов 0 или 1")

        value = int(binary_str, 2)
        return self.get_char_by_value(value)

    def get_value_by_char(self, char: str) -> int:
        """
        Получение числового значения по символу.

        Args:
            char: Символ

        Returns:
            Числовое значение (0-31)
        """
        if char not in self._symbols:
            raise ValueError(f"Символ '{char}' не найден в алфавите")

        return self._symbols[char].value

    # --- Операции замены символов ---

    def replace_symbol(self, value: int, new_char: str) -> TelegraphChar:
        """
        Замена символа в указанном слоте алфавита.

        Телеграфный алфавит всегда содержит 32 слота (0-31).
        Этот метод заменяет символ в указанном слоте на новый.

        Args:
            value: Номер слота (0-31)
            new_char: Новый символ для этого слота

        Returns:
            TelegraphChar: Старый символ, который был заменен
        """
        if not 0 <= value <= 31:
            raise ValueError(f"Значение должно быть от 0 до 31, получено {value}")

        # Сохраняем старый символ для возврата
        old_char_obj = self._codes[value]
        old_char_str = old_char_obj.char

        # Удаляем старый символ из _symbols
        if old_char_str in self._symbols:
            del self._symbols[old_char_str]

        # Создаем новый символ и заменяем в слоте
        self._add_char_object(new_char, value)

        return old_char_obj

    def replace_symbol_by_binary(self, binary_str: str, new_char: str) -> TelegraphChar:
        """
        Замена символа в слоте, указанном бинарной строкой.

        Args:
            binary_str: Бинарная строка (5 символов 0/1), определяющая номер слота
            new_char: Новый символ для этого слота

        Returns:
            TelegraphChar: Старый символ, который был заменен

        Example:
            >>> alphabet.replace_symbol_by_binary('11110', 'Ъ')  # Заменить символ в слоте 30
        """
        if len(binary_str) != 5 or not all(c in '01' for c in binary_str):
            raise ValueError(f"Некорректная бинарная строка: '{binary_str}'. Должно быть 5 символов 0 или 1")

        value = int(binary_str, 2)
        return self.replace_symbol(value, new_char)

    def swap_symbols(self, value1: int, value2: int) -> None:
        """
        Обмен символов между двумя слотами.

        Args:
            value1: Первый слот (0-31)
            value2: Второй слот (0-31)
        """
        if not (0 <= value1 <= 31 and 0 <= value2 <= 31):
            raise ValueError(f"Значения должны быть от 0 до 31")

        # Получаем символы
        char1 = self._codes[value1].char
        char2 = self._codes[value2].char

        # Меняем местами
        self._add_char_object(char1, value2)
        self._add_char_object(char2, value1)

    def reset(self) -> None:
        """
        Сброс алфавита к стандартным значениям.

        Заменяет все символы в слотах на стандартные из DEFAULT_SYMBOLS.
        Размер алфавита остается 32.
        """
        # Очищаем текущие символы
        self._symbols.clear()
        self._codes.clear()

        # Заполняем стандартными символами
        for char, value in self.DEFAULT_SYMBOLS.items():
            self._add_char_object(char, value)

    def build_alphabet(self, key: str) -> 'TelegraphAlphabet':
        """
        Построение рабочего алфавита (таблицы подстановки) по ключевой фразе.

        Алгоритм (Thrithemus_table):
        1. Для каждого символа ключа: если он уже есть в out,
           сдвигаем на следующий символ (mod 32) пока не найдём свободный.
        2. Оставшиеся символы стандартного алфавита добавляются в конец.

        Args:
            key: Ключевая фраза

        Returns:
            Новый TelegraphAlphabet с перестроенным порядком символов
        """
        key_upper = key.upper()
        out = []
        seen = set()

        for ch in key_upper:
            if len(out) >= 32:
                break
            if ch not in self:
                continue
            tmp = ch
            if tmp in seen:
                # tmp = self[(self[tmp].value + 1) % 32].char
                continue
            out.append(tmp)
            seen.add(tmp)

        for char_obj in self:
            if char_obj.char not in seen:
                out.append(char_obj.char)

        new_symbols = {char: idx for idx, char in enumerate(out)}

        return TelegraphAlphabet(new_symbols)

    # --- Арифметические операции ---

    def add_chars(self, char1: str, char2: str) -> TelegraphChar:
        """
        Сложение символов: char1 + char2

        Args:
            char1: Первый символ
            char2: Второй символ

        Returns:
            Результат сложения (TelegraphChar)
        """
        c1 = self.get_char_by_symbol(char1)
        c2 = self.get_char_by_symbol(char2)
        return c1 + c2

    def sub_chars(self, char1: str, char2: str) -> TelegraphChar:
        """
        Вычитание символов: char1 - char2

        Args:
            char1: Первый символ
            char2: Второй символ

        Returns:
            Результат вычитания (TelegraphChar)
        """
        c1 = self.get_char_by_symbol(char1)
        c2 = self.get_char_by_symbol(char2)
        return c1 - c2

    # --- Магические методы (интуитивный интерфейс) ---

    def __getitem__(self, key):
        """
        Доступ к символам через alphabet[ключ].

        Args:
            key: str (символ), int (значение) или slice

        Returns:
            TelegraphChar или список TelegraphChar
        """
        if isinstance(key, str):
            return self.get_char_by_symbol(key)
        elif isinstance(key, int):
            return self.get_char_by_value(key)
        elif isinstance(key, slice):
            # Поддержка срезов: alphabet[0:5]
            start = key.start if key.start is not None else 0
            stop = key.stop if key.stop is not None else 32
            step = key.step if key.step is not None else 1

            result = []
            for i in range(start, stop, step):
                if i in self._codes:
                    result.append(self._codes[i])
            return result
        else:
            raise TypeError(f"Неподдерживаемый тип ключа: {type(key)}")

    def __contains__(self, item):
        """
        Проверка наличия символа в алфавите через 'in'.

        Args:
            item: str (символ) или int (значение)

        Returns:
            bool
        """
        if isinstance(item, str):
            return item in self._symbols
        elif isinstance(item, int):
            return item in self._codes
        elif isinstance(item, TelegraphChar):
            return item.char in self._symbols and self._symbols[item.char] is item
        else:
            return False

    def __len__(self):
        """Количество символов в алфавите"""
        return len(self._symbols)

    def __iter__(self):
        """
        Итерация по символам алфавита.

        Yields:
            TelegraphChar
        """
        # Сортируем по значению для логичного порядка
        for value in sorted(self._codes.keys()):
            yield self._codes[value]

    def items(self):
        """
        Итерация по парам (символ, объект TelegraphChar).

        Yields:
            tuple(str, TelegraphChar)
        """
        # Сортируем по значению для логичного порядка
        for value in sorted(self._codes.keys()):
            char_obj = self._codes[value]
            yield (char_obj.char, char_obj)

    def values(self):
        """
        Итерация по объектам TelegraphChar.

        Yields:
            TelegraphChar
        """
        for value in sorted(self._codes.keys()):
            yield self._codes[value]

    def keys(self):
        """
        Итерация по символам (строкам).

        Yields:
            str
        """
        for value in sorted(self._codes.keys()):
            yield self._codes[value].char

    # --- Вывод информации ---

    def display(self, with_binary=True):
        """
        Вывод алфавита в виде таблицы.

        Args:
            with_binary: Включить ли столбец с бинарным представлением
        """
        print(f"Телеграфный алфавит ({len(self)} символов):")
        print("-" * (60 if with_binary else 40))

        if with_binary:
            print("Символ | Код | Дес. | Бинарник")
            print("-" * 60)
            for char_obj in self:
                print(f"  {char_obj.char:3}  | {char_obj.value:3} | {char_obj.value:3}  | {char_obj.binary}")
        else:
            print("Символ | Код | Дес.")
            print("-" * 40)
            for char_obj in self:
                print(f"  {char_obj.char:3}  | {char_obj.value:3} | {char_obj.value:3}")

        print("-" * (60 if with_binary else 40))

    def __repr__(self):
        """Представление объекта алфавита"""
        return f"TelegraphAlphabet({len(self)} символов)"

    def __str__(self):
        """Строковое представление"""
        symbols = ', '.join([char_obj.char for char_obj in list(self)[:10]])
        if len(self) > 10:
            symbols += ', ...'
        return f"TelegraphAlphabet[{symbols}]"


# ============================================================================
# ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("ДЕМОНСТРАЦИЯ РАБОТЫ С ТЕЛЕГРАФНЫМ АЛФАВИТОМ")
    print("=" * 70)

    # ========================================================================
    # 1. Создание алфавита
    # ========================================================================
    print("\n1. Создание стандартного алфавита:")
    print("-" * 70)

    alphabet = TelegraphAlphabet()
    print(f"Создан алфавит: {alphabet}")
    print(f"Количество символов: {len(alphabet)}")
    alphabet.display()

    # ========================================================================
    # 2. Доступ к символам
    # ========================================================================
    print("\n2. Доступ к символам через alphabet[ключ]:")
    print("-" * 70)

    # Доступ по символу
    char_a = alphabet['А']
    print(f"alphabet['А'] = {char_a} (значение: {char_a.value}, binary: {char_a.binary})")

    # Доступ по значению
    char_5 = alphabet[5]
    print(f"alphabet[5] = {char_5} (символ: {char_5.char}, binary: {char_5.binary})")

    # Доступ через методы
    char_z = alphabet.get_char_by_symbol('З')
    print(f"alphabet.get_char_by_symbol('З') = {char_z}")

    char_bin = alphabet.get_char_by_binary('01000')
    print(f"alphabet.get_char_by_binary('01000') = {char_bin}")

    # Проверка: бинарный код '01000' = десятичное 8 = символ 'З'
    print(f"Проверка: binary '01000' = decimal {int('01000', 2)} = '{char_bin}'")

    # ========================================================================
    # 3. Проверка наличия символов
    # ========================================================================
    print("\n3. Проверка наличия символов через 'in':")
    print("-" * 70)

    print(f"'А' in alphabet: {'А' in alphabet}")
    print(f"'Ё' in alphabet: {'Ё' in alphabet}")
    print(f"1 in alphabet: {1 in alphabet}")
    print(f"50 in alphabet: {50 in alphabet}")

    # ========================================================================
    # 4. Итерация по алфавиту
    # ========================================================================
    print("\n4. Итерация по алфавиту:")
    print("-" * 70)

    print("Первые 10 символов:")
    for i, char_obj in enumerate(alphabet):
        if i >= 10:
            break
        print(f"  {char_obj.char} = {char_obj.value} ({char_obj.binary})")

    print("\nИспользование items():")
    for char_str, char_obj in list(alphabet.items())[:5]:
        print(f"  '{char_str}': value={char_obj.value}, binary={char_obj.binary}")

    # ========================================================================
    # 5. Арифметические операции с символами
    # ========================================================================
    print("\n5. Арифметические операции с символами:")
    print("-" * 70)

    a = alphabet['А']
    z = alphabet['З']

    print(f"a = {a} (значение: {a.value})")
    print(f"z = {z} (значение: {z.value})")
    print(f"a + z = {a + z} (значение: {(a + z).value})")
    print(f"z - a = {z - a} (значение: {(z - a).value})")

    # Операции через методы алфавита
    result1 = alphabet.add_chars('А', 'З')
    result2 = alphabet.sub_chars('Щ', 'З')
    print(f"\nalphabet.add_chars('А', 'З') = {result1}")
    print(f"alphabet.sub_chars('Щ', 'З') = {result2}")

    # Автоматическое приведение типов
    print(f"\nАвтоматическое приведение типов:")
    print(f"a + 'З' = {a + 'З'}")
    print(f"a + 8 = {a + 8}")

    # ========================================================================
    # 6. Операции сравнения
    # ========================================================================
    print("\n6. Операции сравнения:")
    print("-" * 70)

    a1 = alphabet['А']
    a2 = alphabet['А']
    b = alphabet['Б']

    print(f"a1 == a2: {a1 == a2}")
    print(f"a1 is a2: {a1 is a2}")  # Должно быть True, т.к. один объект
    print(f"a1 < b: {a1 < b}")
    print(f"b > a1: {b > a1}")

    # ========================================================================
    # 7. Замена символов в алфавите
    # ========================================================================
    print("\n7. Замена символов в алфавите:")
    print("-" * 70)

    # Создаем копию для экспериментов
    test_alphabet = TelegraphAlphabet()

    print(f"Размер алфавита (всегда фиксирован): {len(test_alphabet)}")
    print(f"Символ в слоте 31: {test_alphabet[31]}")

    # Заменяем символ в слоте
    old_char = test_alphabet.replace_symbol(31, 'Ё')
    print(f"\nЗаменили '{old_char}' на 'Ё' в слоте 31")
    print(f"Размер алфавита: {len(test_alphabet)} (не изменился)")
    print(f"'Я' in test_alphabet: {'Я' in test_alphabet}")
    print(f"'Ё' in test_alphabet: {'Ё' in test_alphabet}")
    print(f"test_alphabet[31] = {test_alphabet[31]}")

    # Замена по бинарному коду
    test_alphabet.replace_symbol_by_binary('11110', 'Ъ')
    print(f"\nЗаменили символ в слоте 30 (binary: 11110) на 'Ъ'")
    print(f"test_alphabet['Ъ'] = {test_alphabet['Ъ']} (binary: {test_alphabet['Ъ'].binary})")

    # Обмен символов между слотами
    print(f"\nДо обмена: alphabet[1]={test_alphabet[1]}, alphabet[2]={test_alphabet[2]}")
    test_alphabet.swap_symbols(1, 2)
    print(f"После обмена: alphabet[1]={test_alphabet[1]}, alphabet[2]={test_alphabet[2]}")

    # ========================================================================
    # 8. Пользовательский алфавит
    # ========================================================================
    print("\n8. Создание пользовательского алфавита:")
    print("-" * 70)

    # Пользовательский алфавит ДОЛЖЕН содержать все 32 символа
    custom_symbols = {
        ' ': 0,   # Пробел
        'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5,
        'F': 6, 'G': 7, 'H': 8, 'I': 9, 'J': 10,
        'K': 11, 'L': 12, 'M': 13, 'N': 14, 'O': 15,
        'P': 16, 'Q': 17, 'R': 18, 'S': 19, 'T': 20,
        'U': 21, 'V': 22, 'W': 23, 'X': 24, 'Y': 25,
        'Z': 26,
        '0': 27, '1': 28, '2': 29, '3': 30, '4': 31
    }

    custom_alphabet = TelegraphAlphabet(custom_symbols)
    print(f"Создан алфавит: {custom_alphabet}")
    print(f"Размер: {len(custom_alphabet)} символов (всегда 32)")
    custom_alphabet.display(with_binary=False)

    # Операции с пользовательским алфавитом
    ca = custom_alphabet['A']
    cb = custom_alphabet['B']
    cc = custom_alphabet['C']
    print(f"\nca = {ca}, cb = {cb}, cc = {cc}")
    print(f"ca + cb = {ca + cb}")
    print(f"cc - ca = {cc - ca}")

    # ========================================================================
    # 9. Срезы (доступ к диапазону слотов)
    # ========================================================================
    print("\n9. Использование срезов:")
    print("-" * 70)

    first_five = alphabet[0:5]
    print(f"alphabet[0:5] = {[str(c) for c in first_five]}")

    last_three = alphabet[29:32]
    print(f"alphabet[29:32] = {[str(c) for c in last_three]}")

    # ========================================================================
    # 10. Сброс алфавита к стандартным значениям
    # ========================================================================
    print("\n10. Сброс алфавита:")
    print("-" * 70)

    test_alphabet2 = TelegraphAlphabet()
    # Заменим несколько символов
    test_alphabet2.replace_symbol(1, 'X')
    test_alphabet2.replace_symbol(2, 'Y')
    test_alphabet2.replace_symbol(3, 'Z')
    print(f"После замен: alphabet[1]={test_alphabet2[1]}, alphabet[2]={test_alphabet2[2]}, alphabet[3]={test_alphabet2[3]}")
    print(f"Размер: {len(test_alphabet2)} (всегда 32)")

    # Сбрасываем к стандартному алфавиту
    test_alphabet2.reset()
    print(f"\nПосле reset():")
    print(f"alphabet[1]={test_alphabet2[1]}, alphabet[2]={test_alphabet2[2]}, alphabet[3]={test_alphabet2[3]}")
    print(f"Размер: {len(test_alphabet2)} (всегда 32, вернулись к стандартным символам)")

    print("\n" + "=" * 70)
    print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 70)