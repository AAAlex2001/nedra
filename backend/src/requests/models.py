"""ORM-модель заявки с сайта."""

from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class Request(Base):
    """Заявка, отправленная через форму на сайте."""

    __tablename__ = "requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    telephone: Mapped[str] = mapped_column(String(32))
    email: Mapped[str] = mapped_column(String(255))
    activity: Mapped[str] = mapped_column(String(64), index=True)
    direction: Mapped[str] = mapped_column(String(64), index=True)
    company_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    inn: Mapped[str | None] = mapped_column(String(32), nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
