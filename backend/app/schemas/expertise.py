from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.expertise import ExpertiseStatus


class ExpertiseInSchema(BaseModel):
    """Заявка на экспертизу. Нужен либо класс опасности, либо категория эксперта."""

    object_code: str = Field(..., max_length=8, description="Объект экспертизы: kl, tp, kl_tp, d, ob")
    area_code: str = Field(..., max_length=8, description="Область аттестации, например Э1")
    hazard_class: int | None = Field(None, ge=1, le=4, description="Класс опасности ОПО")
    expert_category: int | None = Field(None, ge=1, le=3, description="Категория эксперта")
    comment: str | None = Field(None, max_length=4000, description="Комментарий заказчика")


class ExpertiseDocumentSchema(BaseModel):
    """Файл экспертизы. Путь на диске наружу не отдаём."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    kind: str
    original_name: str
    size: int
    content_type: str
    created_at: datetime


class ExpertiseOutSchema(BaseModel):
    """Экспертиза для кабинета заказчика и эксперта."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    customer_name: str
    expert_id: int | None
    object_code: str
    area_code: str
    hazard_class: int | None
    expert_category: int
    comment: str | None
    status: ExpertiseStatus
    created_at: datetime
    documents: list[ExpertiseDocumentSchema]
