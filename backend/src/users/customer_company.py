"""Организация заказчика."""

from dataclasses import dataclass


@dataclass(
    frozen=True,
    kw_only=True,
)
class CustomerCompany:
    """Последние реквизиты заказчика."""

    name: str  # Название организации.
    inn: str  # ИНН организации.
