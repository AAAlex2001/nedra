"""Счёт в личном кабинете."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from src.billing.models.invoice import Invoice
from src.payments.enums import PaymentStage


class InvoiceResponse(BaseModel):
    """Номер, сумма и состояние счёта."""

    id: int  # Номер счёта.
    audit_id: int | None  # Аудит, если счёт относится к нему.
    expertise_id: int | None  # Экспертиза, если счёт относится к ней.
    stage: PaymentStage  # Оплачиваемый этап.
    payer_name: str  # Наименование плательщика.
    payer_inn: str  # ИНН плательщика.
    created_at: datetime  # Дата выставления.
    number: str
    amount: Decimal
    reported_at: datetime | None
    paid_at: datetime | None

    @classmethod
    def from_model(cls, *, invoice: Invoice) -> "InvoiceResponse":
        """Подготовить сведения о счёте."""

        return cls(
            id=invoice.id,
            audit_id=invoice.audit_id,
            expertise_id=invoice.expertise_id,
            stage=invoice.stage,
            payer_name=invoice.payer_name,
            payer_inn=invoice.payer_inn,
            created_at=invoice.created_at,
            number=f"{invoice.created_at.year}-{invoice.id:04d}",
            amount=invoice.amount,
            reported_at=invoice.reported_at,
            paid_at=invoice.paid_at,
        )
