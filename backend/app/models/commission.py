from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class CommissionApplication(Base):
    """Заявка кандидата в эксперты для конкурсной комиссии.

    Приходит из всплывающего окна на сайте: ФИО, телефон, email и список аттестаций —
    область, объект экспертизы и категория. Это не регистрация эксперта:
    аккаунт не создаётся, комиссия разбирает заявки в админке.
    """

    __tablename__ = "commission_applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    full_name: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(32))
    email: Mapped[str] = mapped_column(String(320))

    attestations: Mapped[list[dict]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), default=list
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
