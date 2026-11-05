"""Состояния и этапы оплаты."""

from enum import StrEnum


class PaymentStatus(StrEnum):
    """Состояние платежа у провайдера."""

    PENDING = "pending"
    WAITING_FOR_CAPTURE = "waiting_for_capture"
    SUCCEEDED = "succeeded"
    CANCELED = "canceled"


class PaymentStage(StrEnum):
    """Оплачиваемая часть работы."""

    ADVANCE = "advance"
    FINAL = "final"
