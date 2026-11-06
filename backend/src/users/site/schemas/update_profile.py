"""Изменение профиля."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from src.users.enums import UserRole
from src.users.models.user import User


class UpdateProfileRequest(BaseModel):
    """Новые имя и телефон."""

    full_name: str = Field(
        min_length=2,
        max_length=255,
    )
    phone: str = Field(
        min_length=10,
        max_length=32,
    )

    @field_validator(
        "full_name",
        mode="before",
    )
    @classmethod
    def strip_full_name(cls, full_name: object) -> object:
        """Убрать пробелы вокруг имени."""

        return full_name.strip() if isinstance(full_name, str) else full_name


class UpdateProfileResponse(BaseModel):
    """Профиль текущего пользователя."""

    id: int
    email: EmailStr
    full_name: str
    phone: str
    role: UserRole
    created_at: datetime

    @classmethod
    def from_model(cls, *, user: User) -> "UpdateProfileResponse":
        """Подготовить данные профиля."""

        return cls(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            role=UserRole(user.role),
            created_at=user.created_at,
        )
