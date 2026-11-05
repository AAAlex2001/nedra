"""Уведомления личного кабинета."""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class Notification(Base):
    """Уведомление пользователя."""

    __tablename__ = "notifications"
    __table_args__ = (
        CheckConstraint(
            "num_nonnulls(expertise_id, audit_id) <= 1", name="ck_notification_service"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)  # Номер уведомления.
    user_id: Mapped[int] = mapped_column(  # Получатель.
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        index=True,
    )
    expertise_id: Mapped[int | None] = mapped_column(  # Экспертиза.
        ForeignKey("expertises.id", ondelete="CASCADE"),
        index=True,
    )
    audit_id: Mapped[int | None] = mapped_column(  # Аудит.
        ForeignKey("audits.id", ondelete="CASCADE"),
        index=True,
    )

    kind: Mapped[str | None] = mapped_column(String(32))  # Вид уведомления.
    text: Mapped[str] = mapped_column(String(500))  # Текст уведомления.
    created_at: Mapped[datetime] = mapped_column(  # Дата отправки.
        DateTime(timezone=True),
        server_default=func.now(),
    )
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))  # Дата прочтения.
