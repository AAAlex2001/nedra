"""Вход в личный кабинет."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.auth.options import PASSWORD_MAX_BYTES
from src.users.enums import UserRole
from src.users.models.user import User


class LoginRequest(BaseModel):
    """Почта и пароль пользователя."""

    model_config = ConfigDict(hide_input_in_errors=True)
    email: EmailStr
    password: str = Field(
        max_length=PASSWORD_MAX_BYTES,
        repr=False,
    )


class LoginResponse(BaseModel):
    """Профиль текущего пользователя."""

    id: int
    email: EmailStr
    full_name: str
    phone: str
    role: UserRole
    created_at: datetime

    @classmethod
    def from_model(cls, *, user: User) -> "LoginResponse":
        """Подготовить данные профиля."""

        return cls(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            role=UserRole(user.role),
            created_at=user.created_at,
        )
