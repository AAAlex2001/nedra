"""Реквизиты исполнителя из настроек. Без них документы печатать нельзя."""

from dataclasses import dataclass

from app.config import get_settings


class CompanyRequisitesMissingError(Exception):
    """В настройках не заполнены реквизиты организации."""


@dataclass(frozen=True)
class CompanyRequisites:
    """Наши реквизиты для счёта и акта."""

    name: str
    inn: str
    kpp: str | None
    address: str
    bank: str
    bic: str
    account: str
    corr_account: str
    director: str
    vat_rate: int


def load_requisites() -> CompanyRequisites:
    """Собрать реквизиты из окружения. Бросает CompanyRequisitesMissingError."""

    settings = get_settings()

    required = {
        "COMPANY_INN": settings.company_inn,
        "COMPANY_ADDRESS": settings.company_address,
        "COMPANY_BANK": settings.company_bank,
        "COMPANY_BIC": settings.company_bic,
        "COMPANY_ACCOUNT": settings.company_account,
        "COMPANY_CORR_ACCOUNT": settings.company_corr_account,
        "COMPANY_DIRECTOR": settings.company_director,
    }

    missing = [name for name, value in required.items() if not value]
    if missing:
        raise CompanyRequisitesMissingError(
            "Не заполнены реквизиты организации: " + ", ".join(missing)
        )

    return CompanyRequisites(
        name=settings.company_name,
        inn=str(settings.company_inn),
        kpp=settings.company_kpp,
        address=str(settings.company_address),
        bank=str(settings.company_bank),
        bic=str(settings.company_bic),
        account=str(settings.company_account),
        corr_account=str(settings.company_corr_account),
        director=str(settings.company_director),
        vat_rate=settings.company_vat_rate,
    )
