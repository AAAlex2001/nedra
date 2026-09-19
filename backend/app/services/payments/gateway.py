"""Шлюз ЮKassa: единственное место, где мы ходим в их API.

Остальной код не знает про HTTP и формат ответов ЮKassa — он работает
с GatewayPayment. Если завтра поменяется провайдер, меняется только этот файл.
Документация: https://yookassa.ru/developers/api
"""

from dataclasses import dataclass
from decimal import Decimal

import httpx

from app.services.payments.exceptions import PaymentGatewayError

BASE_URL = "https://api.yookassa.ru/v3"
CURRENCY = "RUB"
TIMEOUT_SECONDS = 15


@dataclass(frozen=True)
class GatewayPayment:
    """Платёж в терминах ЮKassa: только то, что нужно нашему коду."""

    id: str
    status: str
    paid: bool
    confirmation_url: str | None


def parse_payment(data: dict) -> GatewayPayment:
    """Собрать GatewayPayment из JSON-ответа ЮKassa."""

    confirmation = data.get("confirmation")
    confirmation_url = None
    if confirmation is not None:
        confirmation_url = confirmation.get("confirmation_url")

    return GatewayPayment(
        id=data["id"],
        status=data["status"],
        paid=bool(data.get("paid", False)),
        confirmation_url=confirmation_url,
    )


class YooKassaGateway:
    """Создание платежа и запрос его состояния. Авторизация — Basic по shop_id и секретному ключу."""

    def __init__(self, shop_id: str, secret_key: str, vat_code: int) -> None:
        self.auth = (shop_id, secret_key)
        self.vat_code = vat_code

    async def create_payment(
        self,
        amount: Decimal,
        description: str,
        customer_email: str,
        return_url: str,
        idempotence_key: str,
    ) -> GatewayPayment:
        """Создать платёж с редиректом на страницу оплаты ЮKassa.

        capture=True — деньги списываются сразу после оплаты, без ручного
        подтверждения. Idempotence-Key защищает от двойного платежа при
        повторе запроса: на один ключ ЮKassa создаёт один платёж.
        Чек по 54-ФЗ обязателен: одна позиция «услуга» на всю сумму,
        отправляется на email плательщика.
        """

        price = {"value": f"{amount:.2f}", "currency": CURRENCY}

        body = {
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
        headers = {"Idempotence-Key": idempotence_key}

        async with httpx.AsyncClient(
            base_url=BASE_URL, auth=self.auth, timeout=TIMEOUT_SECONDS
        ) as client:
            try:
                response = await client.post("/payments", json=body, headers=headers)
            except httpx.HTTPError as error:
                raise PaymentGatewayError("ЮKassa недоступна") from error

        if response.status_code >= 400:
            raise PaymentGatewayError(
                f"ЮKassa ответила {response.status_code}: {response.text}"
            )

        data = response.json()

        return parse_payment(data)

    async def get_payment(self, payment_id: str) -> GatewayPayment:
        """Актуальное состояние платежа. Именно этому ответу мы доверяем, а не телу уведомления."""

        async with httpx.AsyncClient(
            base_url=BASE_URL, auth=self.auth, timeout=TIMEOUT_SECONDS
        ) as client:
            try:
                response = await client.get(f"/payments/{payment_id}")
            except httpx.HTTPError as error:
                raise PaymentGatewayError("ЮKassa недоступна") from error

        if response.status_code >= 400:
            raise PaymentGatewayError(
                f"ЮKassa ответила {response.status_code}: {response.text}"
            )

        data = response.json()

        return parse_payment(data)
