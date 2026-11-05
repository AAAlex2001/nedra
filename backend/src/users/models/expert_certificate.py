"""Удостоверения экспертов."""

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class ExpertCertificate(Base):
    """Сведения об аттестации эксперта."""

    __tablename__ = "expert_certificates"

    id: Mapped[int] = mapped_column(primary_key=True)  # Номер записи.
    application_id: Mapped[int | None] = mapped_column(  # Заявка на регистрацию.
        ForeignKey(
            "expert_applications.id",
            ondelete="CASCADE",
        ),
        index=True,
    )
    user_id: Mapped[int | None] = mapped_column(  # Аккаунт после одобрения заявки.
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        index=True,
    )
    area_code: Mapped[str] = mapped_column(String(8))  # Область аттестации.
    object_code: Mapped[str] = mapped_column(String(8))  # Вид объекта экспертизы.
    category: Mapped[int] = mapped_column(SmallInteger)  # Категория эксперта.
    valid_until: Mapped[date] = mapped_column(Date)  # Срок действия удостоверения.
    number: Mapped[str | None] = mapped_column(String(64))  # Номер удостоверения или записи ЕРУЛ.
    scan_path: Mapped[str | None] = mapped_column(String(500))  # Путь к ранее загруженному скану.
    scan_name: Mapped[str | None] = mapped_column(String(255))  # Исходное имя скана.
    created_at: Mapped[datetime] = mapped_column(  # Дата добавления.
        DateTime(timezone=True),
        server_default=func.now(),
    )
