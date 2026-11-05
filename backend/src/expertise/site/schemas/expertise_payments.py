"""Оплата экспертизы."""

from datetime import datetime

from pydantic import BaseModel

from src.billing.schemas.invoice import InvoiceResponse
from src.payments.schemas.payment import PaymentResponse


class ExpertisePaymentStageResponse(BaseModel):
    """Оплата одного этапа."""

    paid_at: datetime | None  # Подтверждение оплаты, включая банковский перевод.
    payment: PaymentResponse | None  # Платёж через ЮKassa, если он создан.


class ExpertisePaymentsResponse(BaseModel):
    """Аванс, окончательный расчёт и текущий счёт."""

    advance: ExpertisePaymentStageResponse | None  # Аванс.
    final: ExpertisePaymentStageResponse | None  # Окончательный расчёт.
    invoice: InvoiceResponse | None  # Последний неоплаченный счёт.
