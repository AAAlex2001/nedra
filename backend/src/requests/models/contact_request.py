"""Обращение с сайта."""

from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class ContactRequest(Base):
    """Контакты и выбранная услуга."""

    __tablename__ = "requests"

    id: Mapped[int] = mapped_column(  # Номер обращения.
        primary_key=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255))  # Имя заявителя.
    telephone: Mapped[str] = mapped_column(String(32))  # Контактный телефон.
    email: Mapped[str] = mapped_column(String(320))  # Почта заявителя.
    activity: Mapped[int]  # Код услуги.
    direction: Mapped[int] = mapped_column(index=True)  # Код направления.
    company_name: Mapped[str | None] = mapped_column(String(255))  # Название компании.
    inn: Mapped[str | None] = mapped_column(String(12))  # ИНН компании.
    comment: Mapped[str | None] = mapped_column(String(2000))  # Комментарий заявителя.
    created_at: Mapped[datetime] = mapped_column(  # Дата обращения.
        DateTime(timezone=True),
        server_default=func.now(),
    )
