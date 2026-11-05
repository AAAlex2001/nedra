"""Запросы к API ЮKassa."""

from decimal import Decimal
from urllib.parse import quote

import httpx
from pydantic import ValidationError

from src.payments.exceptions import PaymentGatewayError
from src.payments.options import PAYMENT_CURRENCY
from src.payments.schemas.gateway_payment import GatewayPayment


class YooKassaGateway:
    """Создание и проверка платежей."""

    def __init__(
        self,
        *,
        client: httpx.AsyncClient,
        vat_code: int,
    ) -> None:
        """HTTP-клиент и налоговый код чека."""

        self.client = client
        self.vat_code = vat_code

    async def create_payment(
        self,
        *,
        amount: Decimal,
        description: str,
        customer_email: str,
        return_url: str,
        idempotence_key: str,
    ) -> GatewayPayment:
        """Создать платёж с переходом на оплату."""

        price = {"value": f"{amount:.2f}", "currency": PAYMENT_CURRENCY}
        payload = {
            "amount": price,
            "capture": True,
            "confirmation": {"type": "redirect", "return_url": return_url},
            "description": description,
            "receipt": {
                "customer": {"email": customer_email},
                "items": [
                    {
                        "description": description,
                        "quantity": "1.00",
                        "amount": price,
                        "vat_code": self.vat_code,
                        "payment_subject": "service",
                        "payment_mode": "full_payment",
                    }
                ],
            },
        }

        try:
            response = await self.client.post(
                "/payments",
                json=payload,
                headers={"Idempotence-Key": idempotence_key},
            )
            response.raise_for_status()
            return GatewayPayment.model_validate(response.json())
        except (httpx.HTTPError, ValidationError, ValueError) as error:
            raise PaymentGatewayError() from error

    async def get_payment(self, *, provider_payment_id: str) -> GatewayPayment:
        """Проверить состояние платежа у провайдера."""

        payment_id = quote(provider_payment_id, safe="")

        try:
            response = await self.client.get(f"/payments/{payment_id}")
            response.raise_for_status()
            return GatewayPayment.model_validate(response.json())
        except (httpx.HTTPError, ValidationError, ValueError) as error:
            raise PaymentGatewayError() from error
