"""Уведомление платёжного провайдера."""

from typing import Literal

from pydantic import BaseModel, Field


class WebhookPayment(BaseModel):
    """Номер платежа для проверки."""

    id: str = Field(
        min_length=1,
        max_length=64,
    )


class PaymentWebhookRequest(BaseModel):
    """Событие ЮKassa."""

    type: Literal["notification"]
    event: str
    object: WebhookPayment


class PaymentWebhookResponse(BaseModel):
    """Подтверждение обработки уведомления."""

    status: str = "ok"
