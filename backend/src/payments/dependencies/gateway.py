"""Соединение с платёжным провайдером."""

from collections.abc import AsyncIterator

import httpx
from fastapi import Depends

from src.core.settings import Settings, get_settings
from src.payments.exceptions import PaymentConfigurationError
from src.payments.gateway import YooKassaGateway
from src.payments.options import PAYMENT_TIMEOUT_SECONDS, YOOKASSA_API_URL


async def get_payment_gateway(
    *,
    settings: Settings = Depends(get_settings),
) -> AsyncIterator[YooKassaGateway]:
    """Открыть соединение с провайдером."""

    if not settings.yookassa_shop_id or not settings.yookassa_secret_key:
        raise PaymentConfigurationError()

    async with httpx.AsyncClient(
        base_url=YOOKASSA_API_URL,
        auth=(settings.yookassa_shop_id, settings.yookassa_secret_key),
        timeout=PAYMENT_TIMEOUT_SECONDS,
    ) as client:
        yield YooKassaGateway(
            client=client,
            vat_code=settings.yookassa_vat_code,
        )
