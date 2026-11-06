"""Таблицы реквизитов, работ и подписей."""

from decimal import Decimal
from html import escape

from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Table, TableStyle

from src.documents.money_formatting import format_amount, vat_included
from src.documents.pdf.options import (
    BODY,
    BODY_RIGHT,
    BOLD,
    LINE,
    REGULAR,
    SMALL,
    STRONG,
)


def requisites_table(rows: list[tuple[str, str]]) -> Table:
    """Таблица «подпись — значение» в две колонки без рамок."""

    requisite_rows = [
        [Paragraph(escape(label), SMALL), Paragraph(escape(value), BODY)] for label, value in rows
    ]
    table = Table(requisite_rows, colWidths=(45 * mm, 135 * mm))
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


def items_table(
    subject: str,
    amount: Decimal,
) -> Table:
    """Таблица работ: одна строка на всю сумму."""

    header = ["№", "Наименование работ", "Кол-во", "Ед.", "Цена", "Сумма"]
    price = format_amount(amount)
    row = ["1", Paragraph(escape(subject), BODY), "1", "усл.", price, price]

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


def vat_row(
    amount: Decimal,
    rate: int,
) -> list[Paragraph]:
    """Строка налога: сумма НДС или отметка, что его нет."""

    if rate <= 0:
        return [Paragraph("НДС:", BODY), Paragraph("без НДС", BODY)]

    return [
        Paragraph(f"В том числе НДС {rate} %:", BODY),
        Paragraph(format_amount(vat_included(amount, rate)), BODY),
    ]


def totals(
    amount: Decimal,
    rate: int,
) -> Table:
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


def signature_line(
    label: str,
    name: str,
) -> Table:
    """Строка подписи с линией под ней."""

    table = Table(
        [
            [
                Paragraph(escape(label), BODY),
                Paragraph("", BODY),
                Paragraph(escape(name), BODY_RIGHT),
            ]
        ],
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
