"""Заявки на регистрацию экспертов."""

from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Index, String, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.auth.enums import ApplicationStatus
from src.core.database import Base


class ExpertApplication(Base):
    """Заявка эксперта на регистрацию."""

    __tablename__ = "expert_applications"
    __table_args__ = (
        Index(
            "uq_expert_applications_pending_email",
            "email",
            unique=True,
            postgresql_where=text("status = 'pending'"),
            sqlite_where=text("status = 'pending'"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)  # Номер заявки.
    email: Mapped[str] = mapped_column(  # Почта для входа и связи.
        String(320),
        index=True,
    )
    password_hash: Mapped[str] = mapped_column(String(255))  # Хеш пароля будущего аккаунта.
    full_name: Mapped[str] = mapped_column(String(255))  # ФИО заявителя.
    phone: Mapped[str] = mapped_column(String(32))  # Контактный телефон.
    directions: Mapped[list[str]] = mapped_column(  # Направления работы эксперта.
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
    )
    status: Mapped[str] = mapped_column(  # Результат рассмотрения.
        String(16),
        index=True,
        default=ApplicationStatus.PENDING,
    )
    admin_comment: Mapped[str | None] = mapped_column(String(1000))  # Комментарий администратора.
    user_id: Mapped[int | None] = mapped_column(  # Аккаунт после одобрения.
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
    )
    created_at: Mapped[datetime] = mapped_column(  # Дата подачи.
        DateTime(timezone=True),
        server_default=func.now(),
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(  # Дата рассмотрения.
        DateTime(timezone=True)
    )
