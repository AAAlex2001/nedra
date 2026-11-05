"""Этапы аудита и ответы на предложения."""

from enum import StrEnum


class AuditStatus(StrEnum):
    """Этап аудита."""

    NEW = "new"
    CONSULTATION = "consultation"
    OFFER = "offer"
    COUNTER = "counter"
    EXPERT_READY = "expert_ready"
    CONTRACT = "contract"
    PLAN = "plan"
    PLAN_REVIEW = "plan_review"
    IN_PROGRESS = "in_progress"
    REMARKS = "remarks"
    CONCLUSION_READY = "conclusion_ready"
    PAID = "paid"
    SENT = "sent"
    ACCEPTED = "accepted"


class AuditOfferAnswer(StrEnum):
    """Ответ заказчика на предложение цены."""

    ACCEPT = "accept"
    COUNTER = "counter"
    DECLINE = "decline"
