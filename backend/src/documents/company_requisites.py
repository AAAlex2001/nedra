"""Реквизиты организации-исполнителя."""

from dataclasses import dataclass

from src.core.settings import Settings


class CompanyRequisitesMissingError(Exception):
    """Реквизиты исполнителя не настроены."""


@dataclass(
    frozen=True,
    kw_only=True,
)
class CompanyRequisites:
    """Реквизиты для договора, счёта и акта."""

    name: str  # Наименование исполнителя.
    inn: str  # ИНН исполнителя.
    kpp: str | None  # КПП исполнителя.
    address: str  # Юридический адрес.
    bank: str  # Название банка.
    bic: str  # БИК банка.
    account: str  # Расчётный счёт.
    corr_account: str  # Корреспондентский счёт.
    director: str  # Имя руководителя.
    vat_rate: int  # Ставка НДС.


def load_company_requisites(*, settings: Settings) -> CompanyRequisites:
    """Получить реквизиты из настроек."""

    if not all(
        (
            settings.company_inn,
            settings.company_address,
            settings.company_bank,
            settings.company_bic,
            settings.company_account,
            settings.company_corr_account,
            settings.company_director,
        )
    ):
        raise CompanyRequisitesMissingError()

    return CompanyRequisites(
        name=settings.company_name,
        inn=settings.company_inn,
        kpp=settings.company_kpp,
        address=settings.company_address,
        bank=settings.company_bank,
        bic=settings.company_bic,
        account=settings.company_account,
        corr_account=settings.company_corr_account,
        director=settings.company_director,
        vat_rate=settings.company_vat_rate,
    )
