"""Смена электронной почты."""

from pydantic import BaseModel, EmailStr, Field


class EmailChangeRequest(BaseModel):
    """Новый адрес почты."""

    email: EmailStr


class EmailConfirmationRequest(BaseModel):
    """Код подтверждения из письма."""

    code: str = Field(
        pattern=r"^\s*[0-9]{6}\s*$",
        repr=False,
    )


class EmailCodeSentResponse(BaseModel):
    """Адрес и время до повторной отправки."""

    email: str
    resend_in: int
