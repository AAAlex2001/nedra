from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AttestationSchema(BaseModel):
    """Аттестация кандидата: область, объект экспертизы и категория."""

    area_code: str = Field(..., max_length=8, description="Область аттестации, например Э1")
    object_code: str = Field(..., max_length=8, description="Объект экспертизы: kl, tp, kl_tp, d, ob")
    category: int = Field(..., ge=1, le=3, description="Категория эксперта")


class CommissionApplicationInSchema(BaseModel):
    """Заявка кандидата в конкурсную комиссию."""

    full_name: str = Field(..., min_length=3, max_length=255, description="ФИО кандидата")
    attestations: list[AttestationSchema] = Field(..., min_length=1, max_length=30)


class CommissionApplicationOutSchema(CommissionApplicationInSchema):
    """Заявка кандидата для админки."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
