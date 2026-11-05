"""Данные обращения с сайта."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from src.requests.models.contact_request import ContactRequest


class CreateContactRequest(BaseModel):
    """Новое обращение."""

    name: str = Field(max_length=255)
    telephone: str = Field(max_length=32)
    email: EmailStr
    activity: int
    company_name: str | None = Field(
        default=None,
        max_length=255,
    )
    inn: str | None = Field(
        default=None,
        max_length=12,
    )
    comment: str | None = Field(
        default=None,
        max_length=2000,
    )


class ContactRequestResponse(CreateContactRequest):
    """Сохранённое обращение."""

    request_id: int
    direction: int
    created_at: datetime

    @classmethod
    def from_model(cls, *, contact_request: ContactRequest) -> "ContactRequestResponse":
        """Подготовить данные обращения."""

        return cls(
            request_id=contact_request.id,
            name=contact_request.name,
            telephone=contact_request.telephone,
            email=contact_request.email,
            activity=contact_request.activity,
            direction=contact_request.direction,
            company_name=contact_request.company_name,
            inn=contact_request.inn,
            comment=contact_request.comment,
            created_at=contact_request.created_at,
        )
