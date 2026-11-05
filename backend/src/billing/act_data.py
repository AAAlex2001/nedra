"""Данные акта выполненных работ."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(
    frozen=True,
    kw_only=True,
)
class ActPayer:
    """Реквизиты заказчика для акта."""

    name: str  # Имя или название заказчика.
    details: str  # ИНН или паспортные данные.
    address: str  # Адрес заказчика.


@dataclass(
    frozen=True,
    kw_only=True,
)
class ActData:
    """Содержание акта."""

    number: str  # Номер с обозначением услуги.
    amount: Decimal  # Согласованная стоимость.
    signed_at: datetime  # Дата приёмки.
    subject: str  # Наименование выполненной работы.
    payer: ActPayer  # Реквизиты заказчика.
