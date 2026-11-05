"""Этапы и результаты экспертизы."""

from enum import StrEnum


class ExpertiseStatus(StrEnum):
    """Этап экспертизы."""

    NEW = "new"
    EXPERT_READY = "expert_ready"
    CONTRACT = "contract"
    IN_PROGRESS = "in_progress"
    REMARKS = "remarks"
    CONCLUSION_READY = "conclusion_ready"
    PAID = "paid"
    SENT = "sent"
    ACCEPTED = "accepted"


class ExpertiseResult(StrEnum):
    """Результат экспертизы."""

    POSITIVE = "positive"
    NEGATIVE = "negative"
