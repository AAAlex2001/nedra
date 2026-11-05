"""Подтверждение смены почты."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class EmailChange(Base):
    """Запрос пользователя на смену почты."""

    __tablename__ = "email_changes"

    user_id: Mapped[int] = mapped_column(  # Владелец аккаунта.
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )
    email: Mapped[str] = mapped_column(String(320))  # Новый адрес.
    code_hash: Mapped[str] = mapped_column(String(64))  # Хеш кода подтверждения.
    attempts: Mapped[int] = mapped_column(  # Число неверных попыток.
        SmallInteger,
        default=0,
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))  # Срок действия кода.
    created_at: Mapped[datetime] = mapped_column(  # Дата запроса кода.
        DateTime(timezone=True),
        server_default=func.now(),
    )
