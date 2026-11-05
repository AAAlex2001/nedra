"""Настройки платежей."""

from decimal import Decimal

from src.payments.enums import PaymentStage

YOOKASSA_API_URL = "https://api.yookassa.ru/v3"
PAYMENT_CURRENCY = "RUB"
PAYMENT_TIMEOUT_SECONDS = 15
KOPECK = Decimal("0.01")
STAGE_TITLES = {
    PaymentStage.ADVANCE: "Аванс 50%",
    PaymentStage.FINAL: "Оставшиеся 50%",
}
