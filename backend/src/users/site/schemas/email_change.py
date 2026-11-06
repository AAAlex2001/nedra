"""Запрос смены почты."""

from pydantic import BaseModel, EmailStr


class EmailChangeRequest(BaseModel):
    """Новый адрес почты."""

    email: EmailStr


class EmailCodeSentResponse(BaseModel):
    """Адрес и время до повторной отправки."""

    email: str
    resend_in: int
