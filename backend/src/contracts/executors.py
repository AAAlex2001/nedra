"""Выбор исполнителя по виду договора."""

from src.contracts.enums import ContractKind
from src.contracts.options import SIBNTC_REQUISITES
from src.core.settings import Settings
from src.documents.company_requisites import CompanyRequisites, load_company_requisites


def get_executor_requisites(
    *,
    kind: str | None,
    settings: Settings,
) -> CompanyRequisites:
    """Получить реквизиты исполнителя."""

    if kind == ContractKind.DECLARATION:
        return SIBNTC_REQUISITES

    return load_company_requisites(settings=settings)
