"""Условия для заполнения договора."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from src.contracts.enums import ContractKind


@dataclass(
    frozen=True,
    kw_only=True,
)
class ContractTerms:
    """Реквизиты конкретного договора."""

    number: str  # Номер договора.
    signed_at: datetime  # Дата подписания.
    kind: ContractKind  # Вид договора.
    object_name: str  # Объект работ.
    price: Decimal  # Стоимость работ.
    deadline: str | None  # Желаемый срок.
    vat_rate: int  # Ставка НДС.
    customer_values: dict[str, str]  # Реквизиты для полей шаблона.
