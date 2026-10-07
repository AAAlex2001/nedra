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


class ProfileUpdateSchema(BaseModel):
    """Имя и телефон, которые пользователь меняет в кабинете."""

    full_name: str = Field(..., min_length=2, max_length=255, description="Имя и фамилия")
    phone: str = Field(..., min_length=10, max_length=32, description="Телефон для связи")


class EmailChangeSchema(BaseModel):
    """Новый email, на который отправить код."""

    email: EmailStr = Field(..., description="Новый email")


class EmailCodeSentSchema(BaseModel):
    """Куда ушёл код и через сколько секунд можно запросить новый."""

    email: str = Field(..., description="Адрес, на который отправлен код")
    resend_in: int = Field(..., description="Секунд до истечения кода и повторной отправки")


class EmailConfirmSchema(BaseModel):
    """Код из письма."""

    code: str = Field(..., pattern=r"^\s*\d{6}\s*$", description="Шесть цифр из письма")


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


class CustomerOutSchema(BaseModel):
    """Заказчик в админке: аккаунт, реквизиты организации и число заявок."""

    user_id: int = Field(..., description="ID пользователя")
    email: EmailStr = Field(..., description="Email")
    full_name: str = Field(..., description="Имя и фамилия")
    phone: str = Field(..., description="Телефон")
    created_at: datetime = Field(..., description="Когда зарегистрирован")
    company_name: str | None = Field(None, description="Название организации, если заполнена")
    company_inn: str | None = Field(None, description="ИНН организации, если заполнен")
    expertises_count: int = Field(..., description="Сколько заявок на экспертизу подано")
