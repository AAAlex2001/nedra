"""Изменение аудиторской группы."""

from pydantic import BaseModel, Field


class SetAuditTeamRequest(BaseModel):
    """Номера участников группы."""

    user_ids: list[int] = Field(
        default_factory=list,
        max_length=20,
    )
