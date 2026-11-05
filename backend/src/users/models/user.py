"""Учётная запись пользователя."""

from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class User(Base):
    """Пользователь сервиса."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)  # Идентификатор пользователя.
    email: Mapped[str] = mapped_column(  # Почта для входа и писем.
        String(320),
        unique=True,
        index=True,
    )
    password_hash: Mapped[str] = mapped_column(String(255))  # Хеш пароля.
    full_name: Mapped[str] = mapped_column(String(255))  # Имя и фамилия пользователя.
    phone: Mapped[str] = mapped_column(String(32))  # Контактный телефон.
    role: Mapped[str] = mapped_column(  # Заказчик или эксперт.
        String(16),
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(  # Дата регистрации.
        DateTime(timezone=True),
        server_default=func.now(),
    )
