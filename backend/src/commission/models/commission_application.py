"""Заявка в конкурсную комиссию."""

from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class CommissionApplication(Base):
    """Контакты и аттестации кандидата."""

    __tablename__ = "commission_applications"

    id: Mapped[int] = mapped_column(primary_key=True)  # Номер заявки.
    full_name: Mapped[str] = mapped_column(String(255))  # ФИО кандидата.
    phone: Mapped[str] = mapped_column(String(32))  # Контактный телефон.
    email: Mapped[str] = mapped_column(String(320))  # Почта кандидата.
    attestations: Mapped[list[dict[str, str | int]]] = mapped_column(  # Аттестации.
        JSONB,
        default=list,
    )
    created_at: Mapped[datetime] = mapped_column(  # Дата подачи заявки.
        DateTime(timezone=True),
        server_default=func.now(),
    )
