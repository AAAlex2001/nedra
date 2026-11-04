"""Pydantic-схемы заявок."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.requests.models import Request


class RequestInSchema(BaseModel):
    """Входная схема заявки с сайта."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=255)
    telephone: str = Field(min_length=5, max_length=32)
    email: EmailStr
    activity: str = Field(min_length=1, max_length=64)
    company_name: str | None = Field(default=None, max_length=255)
    inn: str | None = Field(default=None, max_length=32)
    comment: str | None = Field(default=None, max_length=2000)


class RequestOutSchema(BaseModel):
    """Выходная схема заявки."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    telephone: str
    email: str
    activity: str
    direction: str
    company_name: str | None
    inn: str | None
    comment: str | None
    created_at: datetime

    @classmethod
    def from_model(cls, *, model: Request) -> "RequestOutSchema":
        """Создаёт схему из ORM-модели заявки."""

        return cls(
            id=model.id,
            name=model.name,
            telephone=model.telephone,
            email=model.email,
            activity=model.activity,
            direction=model.direction,
            company_name=model.company_name,
            inn=model.inn,
            comment=model.comment,
            created_at=model.created_at,
        )
