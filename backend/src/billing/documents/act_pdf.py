"""Акт выполненных работ в PDF."""

from io import BytesIO
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from src.billing.act_data import ActData
from src.documents.company_requisites import CompanyRequisites
from src.documents.money_formatting import amount_in_words, vat_text
from src.documents.pdf.fonts import register_fonts
from src.documents.pdf.options import BODY, SMALL, TITLE
from src.documents.pdf.tables import (
    items_table,
    requisites_table,
    signature_line,
    totals,
)


def build_act_pdf(
    *,
    act: ActData,
    font_path: Path | None,
    company: CompanyRequisites,
) -> bytes:
    """Собрать PDF акта выполненных работ."""

    register_fonts(configured_path=font_path)

    amount = act.amount
    signed_at = act.signed_at

    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        title=f"Акт {act.number}.pdf",
    )

    elements = [
        Paragraph(
            f"Акт № {act.number} от {signed_at:%d.%m.%Y} сдачи-приёмки выполненных работ",
            TITLE,
        ),
        requisites_table(
            [
                ("Исполнитель", f"{company.name}, ИНН {company.inn}, {company.address}"),
                ("Заказчик", act.payer.details),
                ("Адрес заказчика", act.payer.address),
            ]
        ),
        Spacer(1, 10),
        items_table(act.subject, amount),
        Spacer(1, 6),
        totals(amount, company.vat_rate),
        Spacer(1, 10),
        Paragraph(
            f"Всего оказано услуг на сумму {amount_in_words(amount)}. "
            f"{vat_text(amount, company.vat_rate)}.",
            BODY,
        ),
        Spacer(1, 6),
        Paragraph(
            "Вышеперечисленные работы выполнены полностью и в срок. "
            "Заказчик претензий по объёму, качеству и срокам оказания услуг не имеет.",
            BODY,
        ),
        Spacer(1, 18),
        signature_line("Исполнитель", company.director),
        Spacer(1, 14),
        signature_line("Заказчик", act.payer.name),
        Spacer(1, 10),
        Paragraph(
            "Акт составлен в электронном виде на основании приёмки работы заказчиком "
            "в личном кабинете института.",
            SMALL,
        ),
    ]

    document.build(elements)

    return buffer.getvalue()
