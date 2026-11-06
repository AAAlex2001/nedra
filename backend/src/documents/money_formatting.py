"""Суммы цифрами и прописью."""

from decimal import ROUND_HALF_UP, Decimal

from src.documents.options import (
    HUNDREDS,
    KOPECKS,
    ONES,
    ONES_FEMALE,
    TEENS,
    TENS,
    UNITS,
)


def plural(
    count: int,
    forms: tuple[str, str, str],
) -> str:
    """Форма слова для числа: 1 рубль, 2 рубля, 5 рублей."""

    last_two = count % 100
    last_digit = count % 10

    if 11 <= last_two <= 19:
        return forms[2]
    if last_digit == 1:
        return forms[0]
    if 2 <= last_digit <= 4:
        return forms[1]

    return forms[2]


def group_to_words(
    value: int,
    female: bool,
) -> list[str]:
    """Три разряда числа словами."""

    ones = ONES_FEMALE if female else ONES
    words = []

    if value >= 100:
        words.append(HUNDREDS[value // 100])
        value = value % 100

    if 10 <= value <= 19:
        words.append(TEENS[value - 10])
        return words

    if value >= 20:
        words.append(TENS[value // 10])
        value = value % 10

    if value > 0:
        words.append(ones[value])

    return words


def number_to_words(value: int) -> str:
    """Записать целое число прописью."""

    if value == 0:
        return "ноль"

    words: list[str] = []

    millions = value // 1_000_000
    thousands = value // 1_000 % 1_000
    remainder = value % 1_000

    if millions:
        words.extend(group_to_words(millions, female=False))
        words.append(plural(millions, ("миллион", "миллиона", "миллионов")))

    if thousands:
        words.extend(group_to_words(thousands, female=True))
        words.append(plural(thousands, ("тысяча", "тысячи", "тысяч")))

    if remainder:
        words.extend(group_to_words(remainder, female=False))

    return " ".join(word for word in words if word)


def amount_in_words(amount: Decimal) -> str:
    """Сумма прописью: «Двадцать тысяч рублей 00 копеек»."""

    amount = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    rubles = int(amount)
    kopecks = int((amount - rubles) * 100)

    words = number_to_words(rubles)
    text = f"{words} {plural(rubles, UNITS)} {kopecks:02d} {plural(kopecks, KOPECKS)}"

    return text[0].upper() + text[1:]


def format_amount(amount: Decimal) -> str:
    """Сумма цифрами с пробелами между разрядами: «20 000,00»."""

    amount = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    rubles = int(amount)
    kopecks = int((amount - rubles) * 100)
    grouped = f"{rubles:,}".replace(",", " ")

    return f"{grouped},{kopecks:02d}"


def vat_included(
    amount: Decimal,
    rate: int,
) -> Decimal:
    """НДС в том числе: цена уже с налогом, выделяем его из суммы."""

    if rate <= 0:
        return Decimal("0")

    return (amount * rate / (100 + rate)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def vat_text(
    amount: Decimal,
    rate: int,
) -> str:
    """Фраза про налог для строки под суммой прописью."""

    if rate <= 0:
        return "Без НДС"

    return f"В том числе НДС {rate} % — {format_amount(vat_included(amount, rate))}"
