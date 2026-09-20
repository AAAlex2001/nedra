"""Общие кирпичики для счёта и акта: стили, таблицы, сумма прописью."""

from decimal import ROUND_HALF_UP, Decimal

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Table, TableStyle

from app.services.documents.fonts import BOLD, REGULAR

LINE = colors.HexColor("#b9bdc7")

BODY = ParagraphStyle("body", fontName=REGULAR, fontSize=9, leading=12)
BODY_RIGHT = ParagraphStyle("bodyRight", parent=BODY, alignment=TA_RIGHT)
STRONG = ParagraphStyle("strong", fontName=BOLD, fontSize=9, leading=12)
TITLE = ParagraphStyle("title", fontName=BOLD, fontSize=14, leading=18, spaceAfter=6)
SMALL = ParagraphStyle("small", fontName=REGULAR, fontSize=8, leading=10)

UNITS = ("рубль", "рубля", "рублей")
KOPECKS = ("копейка", "копейки", "копеек")

ONES = ("", "один", "два", "три", "четыре", "пять", "шесть", "семь", "восемь", "девять")
ONES_FEMALE = ("", "одна", "две", "три", "четыре", "пять", "шесть", "семь", "восемь", "девять")
TEENS = (
    "десять", "одиннадцать", "двенадцать", "тринадцать", "четырнадцать",
    "пятнадцать", "шестнадцать", "семнадцать", "восемнадцать", "девятнадцать",
)
TENS = ("", "", "двадцать", "тридцать", "сорок", "пятьдесят", "шестьдесят", "семьдесят", "восемьдесят", "девяносто")
HUNDREDS = ("", "сто", "двести", "триста", "четыреста", "пятьсот", "шестьсот", "семьсот", "восемьсот", "девятьсот")


def plural(count: int, forms: tuple[str, str, str]) -> str:
    """Форма слова для числа: 1 рубль, 2 рубля, 5 рублей."""

    last_two = count % 100
    last = count % 10

    if 11 <= last_two <= 19:
        return forms[2]
    if last == 1:
        return forms[0]
    if 2 <= last <= 4:
        return forms[1]

    return forms[2]


def group_to_words(value: int, female: bool) -> list[str]:
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
    """Целое число словами. Хватает до миллиона, счета крупнее у нас не бывают."""

    if value == 0:
        return "ноль"

    words: list[str] = []

    millions = value // 1_000_000
    thousands = value // 1_000 % 1_000
    rest = value % 1_000

    if millions:
        words.extend(group_to_words(millions, female=False))
        words.append(plural(millions, ("миллион", "миллиона", "миллионов")))

    if thousands:
        words.extend(group_to_words(thousands, female=True))
        words.append(plural(thousands, ("тысяча", "тысячи", "тысяч")))

    if rest:
        words.extend(group_to_words(rest, female=False))

    return " ".join(word for word in words if word)


def amount_in_words(amount: Decimal) -> str:
    """Сумма прописью: «Двадцать тысяч рублей 00 копеек»."""

    rubles = int(amount)
    kopecks = int((amount - rubles) * 100)

    words = number_to_words(rubles)
    text = f"{words} {plural(rubles, UNITS)} {kopecks:02d} {plural(kopecks, KOPECKS)}"

    return text[0].upper() + text[1:]


def format_amount(amount: Decimal) -> str:
    """Сумма цифрами с пробелами между разрядами: «20 000,00»."""

    rubles = int(amount)
    kopecks = int((amount - rubles) * 100)
    grouped = f"{rubles:,}".replace(",", " ")

    return f"{grouped},{kopecks:02d}"


def vat_included(amount: Decimal, rate: int) -> Decimal:
    """НДС в том числе: цена уже с налогом, выделяем его из суммы."""

    if rate <= 0:
        return Decimal("0")

    return (amount * rate / (100 + rate)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def vat_text(amount: Decimal, rate: int) -> str:
    """Фраза про налог для строки под суммой прописью."""

    if rate <= 0:
        return "Без НДС"

    return f"В том числе НДС {rate} % — {format_amount(vat_included(amount, rate))}"


def requisites_table(rows: list[tuple[str, str]]) -> Table:
    """Таблица «подпись — значение» в две колонки без рамок."""

    data = [[Paragraph(label, SMALL), Paragraph(value, BODY)] for label, value in rows]
    table = Table(data, colWidths=(45 * mm, 135 * mm))
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )

    return table


def items_table(subject: str, amount: Decimal) -> Table:
    """Таблица работ: одна строка на всю сумму."""

    header = ["№", "Наименование работ", "Кол-во", "Ед.", "Цена", "Сумма"]
    price = format_amount(amount)
    row = ["1", Paragraph(subject, BODY), "1", "усл.", price, price]

    table = Table(
        [header, row],
        colWidths=(10 * mm, 90 * mm, 15 * mm, 15 * mm, 25 * mm, 25 * mm),
        repeatRows=1,
    )
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, 0), BOLD),
                ("FONTNAME", (0, 1), (-1, -1), REGULAR),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, LINE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    return table


def vat_row(amount: Decimal, rate: int) -> list[Paragraph]:
    """Строка налога: сумма НДС или отметка, что его нет."""

    if rate <= 0:
        return [Paragraph("НДС:", BODY), Paragraph("без НДС", BODY)]

    return [
        Paragraph(f"В том числе НДС {rate} %:", BODY),
        Paragraph(format_amount(vat_included(amount, rate)), BODY),
    ]


def totals(amount: Decimal, rate: int) -> Table:
    """Итоговые строки справа под таблицей работ."""

    rows = [
        [Paragraph("Итого:", STRONG), Paragraph(format_amount(amount), STRONG)],
        vat_row(amount, rate),
        [Paragraph("Всего к оплате:", STRONG), Paragraph(format_amount(amount), STRONG)],
    ]
    table = Table(rows, colWidths=(155 * mm, 25 * mm))
    table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )

    return table


def signature_line(label: str, name: str) -> Table:
    """Строка подписи с линией под ней."""

    table = Table(
        [[Paragraph(label, BODY), Paragraph("", BODY), Paragraph(name, BODY_RIGHT)]],
        colWidths=(50 * mm, 70 * mm, 60 * mm),
    )
    table.setStyle(
        TableStyle(
            [
                ("LINEBELOW", (1, 0), (1, 0), 0.5, LINE),
                ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )

    return table
