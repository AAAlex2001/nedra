"""Создание произвольного платежа."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from src.payments.models.payment import Payment


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


class CreatePaymentResponse(BaseModel):
    """Сумма, состояние и ссылка на оплату."""

    id: int
    amount: Decimal
    currency: str
    description: str
    status: str
    confirmation_url: str | None
    created_at: datetime
    paid_at: datetime | None

    @classmethod
    def from_model(cls, *, payment: Payment) -> "CreatePaymentResponse":
        """Подготовить сведения о платеже."""

        return cls(
            id=payment.id,
            amount=payment.amount,
            currency=payment.currency,
            description=payment.description,
            status=payment.status,
            confirmation_url=payment.confirmation_url,
            created_at=payment.created_at,
            paid_at=payment.paid_at,
        )
