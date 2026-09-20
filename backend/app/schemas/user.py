from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole

PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 72


class RegisterSchema(BaseModel):
    """Данные формы регистрации."""

    email: EmailStr = Field(..., description="Email, он же логин")
    password: str = Field(
        ...,
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
        description="Пароль, от 8 до 72 символов",
    )
    full_name: str = Field(..., min_length=2, max_length=255, description="Имя и фамилия")
    phone: str = Field(..., min_length=10, max_length=32, description="Телефон для связи")


class LoginSchema(BaseModel):
    """Данные формы входа."""

    email: EmailStr = Field(..., description="Email, указанный при регистрации")
    password: str = Field(..., max_length=PASSWORD_MAX_LENGTH, description="Пароль")


class UserOutSchema(BaseModel):
    """Публичные данные пользователя. Хеш пароля наружу не отдаём.

    Роль у аккаунта одна и задаётся при создании: заказчик регистрируется сам,
    эксперт появляется после одобрения заявки.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="ID пользователя")
    email: EmailStr = Field(..., description="Email")
    full_name: str = Field(..., description="Имя и фамилия")
    phone: str = Field(..., description="Телефон")
    role: UserRole = Field(..., description="Роль аккаунта")
    created_at: datetime = Field(..., description="Когда зарегистрирован")
