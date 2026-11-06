"""Уведомления платёжного провайдера."""

from fastapi import APIRouter, Depends

from src.payments.site.dependencies.webhook import get_process_payment_webhook_usecase
from src.payments.site.schemas.webhook import (
    PaymentWebhookRequest,
    PaymentWebhookResponse,
)
from src.payments.site.usecases.process_webhook import ProcessPaymentWebhookUseCase

router = APIRouter(
    prefix="/payments",
    tags=["payments"],
)


@router.post("/yookassa/webhook")
async def process_payment_webhook(
    *,
    payload: PaymentWebhookRequest,
    usecase: ProcessPaymentWebhookUseCase = Depends(get_process_payment_webhook_usecase),
) -> PaymentWebhookResponse:
    """Проверить уведомление провайдера."""

    await usecase.execute(provider_payment_id=payload.object.id)

    return PaymentWebhookResponse()
