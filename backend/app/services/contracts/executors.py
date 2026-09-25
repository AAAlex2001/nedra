"""Организации-исполнители.

Экспертизу деклараций институт «Недра» не проводит, по ним договор, счёт
и акт оформляются на СибНТЦ «Промтехэксперт». Оплата картой идёт через кассу
«Недр», поэтому для СибНТЦ доступна только оплата по счёту.
"""

from dataclasses import dataclass

from app.models.expertise import ContractKind
from app.services.documents.company import CompanyRequisites, load_requisites


@dataclass(frozen=True)
class Executor:
    """Исполнитель по договору: его шаблоны договора и соглашения о конфиденциальности
    и можно ли платить картой."""

    code: str
    contract_template: str
    nda_template: str
    card_payment: bool


NEDRA = Executor("nedra", "contract_nedra.docx", "nda_nedra.docx", card_payment=True)
SIBNTC = Executor("sibntc", "contract_sibntc.docx", "nda_sibntc.docx", card_payment=False)

SIBNTC_REQUISITES = CompanyRequisites(
    name="ООО «СибНТЦ «Промтехэксперт»",
    inn="4217102012",
    kpp="421701001",
    address=(
        "654005, Кемеровская область, город Новокузнецк, Центральный район, "
        "ул. Орджоникидзе, дом 20, помещение № 7"
    ),
    bank="Филиал «ЦЕНТРАЛЬНЫЙ» Банка ВТБ (ПАО) в г. Москве",
    bic="044525411",
    account="40702810837070000801",
    corr_account="30101810145250000411",
    director="Д.С. Ильчук",
    vat_rate=7,
)


def executor_for(kind: str | None) -> Executor:
    """Исполнитель по виду договора. Пока вид не определён, считаем исполнителем «Недра»."""

    if kind == ContractKind.DECLARATION:
        return SIBNTC

    return NEDRA


def executor_requisites(executor: Executor) -> CompanyRequisites:
    """Реквизиты исполнителя. Реквизиты «Недр» берутся из окружения.

    Бросает CompanyRequisitesMissingError.
    """

    if executor == SIBNTC:
        return SIBNTC_REQUISITES

    return load_requisites()
