"""Даты этапов аудита."""

from datetime import datetime

from pydantic import BaseModel

from src.audit.models.audit import Audit


class AuditDatesResponse(BaseModel):
    """Даты выполнения работы."""

    created_at: datetime  # Подача заявки.
    lead_ready_at: datetime | None  # Согласие руководителя выполнить работу.
    conclusion_ready_at: datetime | None  # Готовность заключения.
    sent_at: datetime | None  # Передача заключения.
    accepted_at: datetime | None  # Приёмка заказчиком.

    @classmethod
    def from_model(cls, *, audit: Audit) -> "AuditDatesResponse":
        """Даты этапов аудита."""

        return cls(
            created_at=audit.created_at,
            lead_ready_at=audit.lead_ready_at,
            conclusion_ready_at=audit.conclusion_ready_at,
            sent_at=audit.sent_at,
            accepted_at=audit.accepted_at,
        )
