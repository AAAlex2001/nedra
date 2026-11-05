"""Даты этапов экспертизы."""

from datetime import datetime

from pydantic import BaseModel

from src.expertise.models.expertise import Expertise


class ExpertiseDatesResponse(BaseModel):
    """Даты выполнения работы."""

    created_at: datetime  # Подача заявки.
    expert_ready_at: datetime | None  # Согласие эксперта выполнить работу.
    conclusion_ready_at: datetime | None  # Готовность заключения.
    sent_at: datetime | None  # Передача заключения.
    accepted_at: datetime | None  # Приёмка заказчиком.

    @classmethod
    def from_model(cls, *, expertise: Expertise) -> "ExpertiseDatesResponse":
        """Даты этапов экспертизы."""

        return cls(
            created_at=expertise.created_at,
            expert_ready_at=expertise.expert_ready_at,
            conclusion_ready_at=expertise.conclusion_ready_at,
            sent_at=expertise.sent_at,
            accepted_at=expertise.accepted_at,
        )
