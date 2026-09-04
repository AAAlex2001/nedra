from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RequestInSchema(BaseModel):
    """Схема запроса."""

    name: str = Field(..., max_length=255, description="Имя того, кто оставляет заявку")
    telephone: str = Field(..., max_length=32, description="Телефон того, кто оставляет заявку")
    email: EmailStr = Field(..., description="Email того, кто оставляет заявку")
    activity: int = Field(..., description="Деятельность, по которой оставляется заявка")
    company_name: str | None = Field(None, max_length=255, description="Название компании того, кто оставляет заявку, если есть")
    inn: str | None = Field(None, max_length=12, description="ИНН компании того, кто оставляет зявку, если есть")
    comment: str | None = Field(None, max_length=2000, description="Комментарий к заявке, если он есть")


class RequestOutSchema(RequestInSchema):
    """Схема ответа."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    request_id: int = Field(..., validation_alias="id", description="ID заявки")
    direction: int = Field(..., description="Направление, вычисленное по виду деятельности")
    created_at: datetime = Field(..., description="Когда заявка создана")
