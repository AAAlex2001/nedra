"""Анкета аудита."""

from pydantic import BaseModel

from src.audit.schemas.audit_details import AuditDetailsSchema


class AuditApplicationResponse(BaseModel):
    """Объект и заполненная анкета."""

    object_name: str | None  # Наименование объекта для договора.
    details: AuditDetailsSchema | None  # Ответы заказчика.
