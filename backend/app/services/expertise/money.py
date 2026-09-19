"""Деление стоимости экспертизы на два платежа."""

from decimal import ROUND_HALF_UP, Decimal

KOPECK = Decimal("0.01")


def split_price(price: Decimal) -> tuple[Decimal, Decimal]:
    """Аванс и остаток по 50 %. Копейка при нечётной сумме уходит в остаток."""

    advance = (price / 2).quantize(KOPECK, rounding=ROUND_HALF_UP)
    final = price - advance

    return advance, final
