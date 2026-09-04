from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Request(Base):
    __tablename__ = "requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    name: Mapped[str] = mapped_column(String(255))
    telephone: Mapped[str] = mapped_column(String(32))
    email: Mapped[str] = mapped_column(String(320))

    activity: Mapped[int] = mapped_column(Integer)
    direction: Mapped[int] = mapped_column(Integer, index=True)

    company_name: Mapped[str | None] = mapped_column(String(255))
    inn: Mapped[str | None] = mapped_column(String(12))
    comment: Mapped[str | None] = mapped_column(String(2000))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
