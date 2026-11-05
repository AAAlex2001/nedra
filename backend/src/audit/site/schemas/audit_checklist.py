"""Перечень документов для аудита."""

from pydantic import BaseModel


class AuditChecklistItemResponse(BaseModel):
    """Пункт перечня документов."""

    number: int
    title: str
