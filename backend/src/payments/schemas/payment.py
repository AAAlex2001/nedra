"""Платёж в личном кабинете."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from src.payments.models.payment import Payment


class PaymentResponse(BaseModel):
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
    def from_model(cls, *, payment: Payment) -> "PaymentResponse":
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
