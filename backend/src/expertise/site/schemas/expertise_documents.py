"""Документы и замечания экспертизы."""

from datetime import datetime

from pydantic import BaseModel, Field

from src.expertise.models.expertise_document import ExpertiseDocument
from src.expertise.models.expertise_remark import ExpertiseRemark


class ExpertiseDocumentResponse(BaseModel):
    """Сведения о файле без пути на диске."""

    id: int
    kind: str
    item_number: int | None
    original_name: str
    size: int
    content_type: str
    created_at: datetime

    @classmethod
    def from_model(cls, *, document: ExpertiseDocument) -> "ExpertiseDocumentResponse":
        """Подготовить сведения о документе."""

        return cls(
            id=document.id,
            kind=document.kind,
            item_number=document.item_number,
            original_name=document.original_name,
            size=document.size,
            content_type=document.content_type,
            created_at=document.created_at,
        )


class ExpertiseRemarkResponse(BaseModel):
    """Замечание и ответ заказчика."""

    id: int
    text: str | None
    response_text: str | None
    created_at: datetime
    resolved_at: datetime | None
    documents: list[ExpertiseDocumentResponse] = Field(default_factory=list)

    @classmethod
    def from_model(
        cls,
        *,
        remark: ExpertiseRemark,
        documents: list[ExpertiseDocumentResponse],
    ) -> "ExpertiseRemarkResponse":
        """Подготовить замечание с приложениями."""

        return cls(
            id=remark.id,
            text=remark.text,
            response_text=remark.response_text,
            created_at=remark.created_at,
            resolved_at=remark.resolved_at,
            documents=documents,
        )
