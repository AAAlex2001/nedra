"""Реквизиты и суммы в шаблоне договора."""

from datetime import datetime
from decimal import Decimal

from src.contracts.options import DEADLINE_DAYS, DEFAULT_DAYS, MONTHS, WORKING_DAYS
from src.contracts.schemas.company import CompanyDetails
from src.documents.money_formatting import (
    amount_in_words,
    format_amount,
    number_to_words,
    plural,
    vat_included,
)
from src.documents.text_formatting import format_initials
from src.expertise.schemas.individual import IndividualDetails
from src.users.models.user import User


def format_date(moment: datetime) -> str:
    """Дата как в договоре: «25» сентября 2026 г."""

    return f"«{moment.day:02d}» {MONTHS[moment.month - 1]} {moment.year} г."


def working_days(deadline: str | None) -> str:
    """Срок из пожелания заказчика: «3 (три) рабочих дня»."""

    days = DEADLINE_DAYS.get(deadline or "", DEFAULT_DAYS)

    return f"{days} ({number_to_words(days)}) {plural(days, WORKING_DAYS)}"


def money_text(amount: Decimal) -> str:
    """Сумма цифрами и прописью: «20 000,00 (Двадцать тысяч рублей 00 копеек)»."""

    return f"{format_amount(amount)} ({amount_in_words(amount)})"


def vat_clause(
    amount: Decimal,
    rate: int,
) -> str:
    """Фраза про НДС в пункте о стоимости."""

    if rate <= 0:
        return "НДС не облагается"

    return f"в т.ч. НДС {rate}% – {money_text(vat_included(amount, rate))}"


def number_requisite_lines(
    prefix: str,
    lines: list[str],
) -> dict[str, str]:
    """Строки блока реквизитов как метки prefix_1, prefix_2…"""

    return {f"{prefix}_{index}": line for index, line in enumerate(lines, start=1)}


def company_template_values(
    company: CompanyDetails,
    customer: User,
) -> dict[str, str]:
    """Преамбулы, реквизиты и подпись для заказчика-юрлица."""

    kpp = company.kpp or "—"
    inn_line = f"ИНН/КПП {company.inn}/{kpp}"
    person = (
        f"{company.full_name} ({company.name}), в лице {company.signer_genitive}, "
        f"действующего на основании {company.signer_basis}"
    )

    contract_lines = [
        company.name,
        inn_line,
        f"ОГРН {company.ogrn}",
        f"Юридический/фактический адрес: {company.address}",
        f"р/с {company.account}",
        f"БАНК {company.bank}",
        f"к/с {company.corr_account}",
        f"БИК {company.bic}",
    ]
    nda_lines = [
        f"Наименование: {company.name}",
        f"Адрес, указанный в ЕГРЮЛ: {company.address}",
        "",
        f"Телефон: {customer.phone}",
        f"Электронная почта: {customer.email}",
        f"ОГРН {company.ogrn}",
        inn_line,
    ]

    return {
        "customer_preamble": f"{person}, именуемое в дальнейшем «Заказчик», с одной стороны,",
        "nda_preamble": f"{person}, далее именуемое Сторона, передающая информацию "
        "(Сторона 1), с одной стороны и",
        "customer_name": company.name,
        "signer_position": company.signer_position,
        "signer_initials": format_initials(full_name=company.signer_name),
        **number_requisite_lines("customer_line", contract_lines),
        **number_requisite_lines("nda_line", nda_lines),
    }


def individual_template_values(
    individual: IndividualDetails,
    customer: User,
) -> dict[str, str]:
    """Преамбулы, реквизиты и подпись для заказчика-физлица."""

    issued = f"{individual.passport_issued_by}, {individual.passport_issued_at:%d.%m.%Y}"
    person = (
        f"{individual.full_name}, паспорт {individual.passport_number}, выдан {issued}, "
        f"адрес регистрации: {individual.address}"
    )

    contract_lines = [
        individual.full_name,
        f"Паспорт: {individual.passport_number}",
        f"Выдан: {issued}",
        f"Адрес регистрации: {individual.address}",
        f"Телефон: {customer.phone}",
        f"E-mail: {customer.email}",
        "",
        "",
    ]
    nda_lines = [
        f"ФИО: {individual.full_name}",
        f"Адрес регистрации: {individual.address}",
        f"Паспорт: {individual.passport_number}, выдан {issued}",
        f"Телефон: {customer.phone}",
        f"Электронная почта: {customer.email}",
        "",
        "",
    ]

    return {
        "customer_preamble": f"{person}, именуемый в дальнейшем «Заказчик», с одной стороны,",
        "nda_preamble": f"{person}, далее именуемый Сторона, передающая информацию "
        "(Сторона 1), с одной стороны и",
        "customer_name": individual.full_name,
        "signer_position": "Заказчик",
        "signer_initials": format_initials(full_name=individual.full_name),
        **number_requisite_lines("customer_line", contract_lines),
        **number_requisite_lines("nda_line", nda_lines),
    }
