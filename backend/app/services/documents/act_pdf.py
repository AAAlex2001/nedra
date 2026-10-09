"""Акт выполненных работ в PDF."""

from dataclasses import dataclass
from decimal import Decimal
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from app.models.expertise import Expertise, uses_company
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


def act_number(expertise: Expertise) -> str:
    """Номер акта совпадает с номером экспертизы, год берём из даты приёмки."""

    year = expertise.accepted_at.year if expertise.accepted_at else expertise.created_at.year

    return f"{year}-{expertise.id:04d}"


def act_filename(expertise: Expertise) -> str:
    """Имя файла для скачивания."""

    return f"Акт {act_number(expertise)}.pdf"


@dataclass(frozen=True)
class ActPayer:
    """Заказчик в акте: как подписан, чем идентифицирован и где зарегистрирован."""

    name: str
    details: str
    address: str


def act_payer(expertise: Expertise) -> ActPayer | None:
    """Заказчик из заявки: организация у юрлица, паспортные данные у физлица."""

    company = expertise.company
    if uses_company(expertise.customer_type) and company is not None:
        kpp = company.kpp or "—"
        return ActPayer(company.name, f"{company.name}, ИНН {company.inn}, КПП {kpp}", company.address)

    individual = expertise.individual
    if individual is not None:
        details = f"{individual.full_name}, паспорт {individual.passport_number}"
        return ActPayer(individual.full_name, details, individual.address)

    return None


def build_act_pdf(
    expertise: Expertise,
    payer: ActPayer,
    subject: str,
    company: CompanyRequisites,
) -> bytes:
    """Собрать PDF акта выполненных работ."""

    register_fonts()

    amount = expertise.price if expertise.price is not None else Decimal("0")
    signed = expertise.accepted_at or expertise.created_at

    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        title=act_filename(expertise),
    )

    flow = [
        Paragraph(
            f"Акт № {act_number(expertise)} от {signed:%d.%m.%Y} сдачи-приёмки выполненных работ",
            TITLE,
        ),
        requisites_table(
            [
                ("Исполнитель", f"{company.name}, ИНН {company.inn}, {company.address}"),
                ("Заказчик", payer.details),
                ("Адрес заказчика", payer.address),
            ]
        ),
        Spacer(1, 10),
        items_table(subject, amount),
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
        signature_line("Заказчик", payer.name),
        Spacer(1, 10),
        Paragraph(
            "Акт составлен в электронном виде на основании приёмки работы заказчиком "
            "в личном кабинете сервиса «Блиц-эксперт».",
            SMALL,
        ),
    ]

    document.build(flow)

    return buffer.getvalue()
