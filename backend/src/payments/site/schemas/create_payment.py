"""Создание произвольного платежа."""

from decimal import Decimal

from pydantic import BaseModel, Field


class CreatePaymentRequest(BaseModel):
    """Сумма и назначение оплаты."""

    amount: Decimal = Field(
        gt=0,
        max_digits=10,
        decimal_places=2,
    )
    description: str = Field(
        min_length=3,
        max_length=128,
    )
