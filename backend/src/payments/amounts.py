"""Суммы аванса и окончательного расчёта."""

from decimal import ROUND_HALF_UP, Decimal

from src.payments.enums import PaymentStage
from src.payments.options import KOPECK


def stage_amount(
    *,
    price: Decimal,
    stage: PaymentStage,
) -> Decimal:
    """Рассчитать сумму выбранного этапа."""

    advance = (price / 2).quantize(KOPECK, rounding=ROUND_HALF_UP)

    if stage == PaymentStage.ADVANCE:
        return advance

    return price - advance
