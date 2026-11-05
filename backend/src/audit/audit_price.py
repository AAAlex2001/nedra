"""Проверка и отображение стоимости."""

from decimal import Decimal

from src.audit.exceptions import InvalidAuditPriceError
from src.audit.options import MAX_AUDIT_PRICE, MIN_AUDIT_PRICE, PRICE_STEP


def validate_audit_price(*, price: Decimal) -> None:
    """Проверить сумму предложения."""

    if not price.is_finite():
        raise InvalidAuditPriceError("Укажите корректную сумму")

    if price < MIN_AUDIT_PRICE or price > MAX_AUDIT_PRICE:
        raise InvalidAuditPriceError("Стоимость аудита — от 100 000 до 99 999 999,99 ₽")

    if price != price.quantize(PRICE_STEP):
        raise InvalidAuditPriceError("Укажите сумму с точностью до копейки")


def format_audit_price(*, price: Decimal) -> str:
    """Представить сумму в рублях."""

    return f"{price:,.2f}".replace(",", " ").replace(".", ",")
