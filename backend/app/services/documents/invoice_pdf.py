"""Счёт на оплату в PDF."""

from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from app.models.billing import Invoice
from app.services.documents.company import CompanyRequisites
from app.services.documents.fonts import register_fonts
from app.services.documents.layout import (
    BODY,
    SMALL,
    TITLE,
    amount_in_words,
    items_table,
    requisites_table,
    signature_line,
    totals,
    vat_text,
)


def invoice_number(invoice: Invoice) -> str:
    """Человеческий номер счёта: год и порядковый номер."""

    return f"{invoice.created_at.year}-{invoice.id:04d}"


def invoice_filename(invoice: Invoice) -> str:
    """Имя файла для скачивания."""

    return f"Счёт {invoice_number(invoice)}.pdf"


def build_invoice_pdf(invoice: Invoice, subject: str, company: CompanyRequisites) -> bytes:
    """Собрать PDF счёта на оплату."""

    register_fonts()

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

    issued = invoice.created_at.strftime("%d.%m.%Y")
    payer_kpp = invoice.payer_kpp or "—"

    flow = [
        Paragraph("Образец заполнения платёжного поручения", SMALL),
        Spacer(1, 4),
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
        Paragraph(f"Счёт на оплату № {invoice_number(invoice)} от {issued}", TITLE),
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
        Spacer(1, 12),
        signature_line("Главный бухгалтер", company.director),
    ]

    document.build(flow)

    return buffer.getvalue()


def stage_subject(expertise_id: int, stage_title: str, description: str) -> str:
    """Текст строки работ: что и за какой этап платят."""

    return f"{stage_title} за экспертизу промышленной безопасности №{expertise_id}. {description}"
