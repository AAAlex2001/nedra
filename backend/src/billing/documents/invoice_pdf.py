"""Счёт на оплату в PDF."""

from io import BytesIO
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from src.billing.models.invoice import Invoice
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


def invoice_number(invoice: Invoice) -> str:
    """Человеческий номер счёта: год и порядковый номер."""

    return f"{invoice.created_at.year}-{invoice.id:04d}"


def invoice_filename(invoice: Invoice) -> str:
    """Имя файла для скачивания."""

    return f"Счёт {invoice_number(invoice)}.pdf"


def build_invoice_pdf(
    *,
    invoice: Invoice,
    subject: str,
    company: CompanyRequisites,
    font_path: Path | None,
) -> bytes:
    """Собрать PDF счёта на оплату."""

    register_fonts(configured_path=font_path)

    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        title=invoice_filename(invoice),
    )

    issued_date = invoice.created_at.strftime("%d.%m.%Y")
    payer_kpp = invoice.payer_kpp or "—"

    elements = [
        requisites_table(
            [
                ("Банк получателя", company.bank),
                ("БИК", company.bic),
                ("Корр. счёт", company.corr_account),
                ("Получатель", f"{company.name}, ИНН {company.inn}, КПП {company.kpp or '—'}"),
                ("Расчётный счёт", company.account),
            ]
        ),
        Spacer(1, 10),
        Paragraph(f"Счёт на оплату № {invoice_number(invoice)} от {issued_date}", TITLE),
        requisites_table(
            [
                ("Исполнитель", f"{company.name}, ИНН {company.inn}, {company.address}"),
                ("Заказчик", f"{invoice.payer_name}, ИНН {invoice.payer_inn}, КПП {payer_kpp}"),
                ("Адрес заказчика", invoice.payer_address),
            ]
        ),
        Spacer(1, 10),
        items_table(subject, invoice.amount),
        Spacer(1, 6),
        totals(invoice.amount, company.vat_rate),
        Spacer(1, 10),
        Paragraph(
            f"Всего наименований 1, на сумму {amount_in_words(invoice.amount)}. "
            f"{vat_text(invoice.amount, company.vat_rate)}.",
            BODY,
        ),
        Spacer(1, 4),
        Paragraph(
            "Счёт действителен к оплате в течение 5 банковских дней. "
            "В назначении платежа укажите номер счёта.",
            SMALL,
        ),
        Spacer(1, 18),
        signature_line("Руководитель", company.director),
    ]

    document.build(elements)

    return buffer.getvalue()


def describe_invoice_stage(
    *,
    work_id: int,
    stage_title: str,
    work_name: str,
    description: str,
) -> str:
    """Текст строки работ: что и за какой этап платят."""

    return f"{stage_title} за {work_name} №{work_id}. {description}"
