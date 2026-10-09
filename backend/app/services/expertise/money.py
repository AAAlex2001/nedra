"""Деление стоимости на два платежа и сумма в рублях для писем и уведомлений."""

from decimal import ROUND_HALF_UP, Decimal

KOPECK = Decimal("0.01")


def format_rub(amount: Decimal | None, empty: str = "по запросу") -> str:
    """Сумма без копеек с разделителем тысяч: 150 000 ₽."""

    if amount is None:
        return empty

    return f"{int(amount):,} ₽".replace(",", " ")


def split_price(price: Decimal) -> tuple[Decimal, Decimal]:
    """Аванс и остаток по 50 %. Копейка при нечётной сумме уходит в остаток."""

    advance = (price / 2).quantize(KOPECK, rounding=ROUND_HALF_UP)
    final = price - advance

    return advance, final
