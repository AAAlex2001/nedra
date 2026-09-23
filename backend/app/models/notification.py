from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.expertise import Expertise


class Notification(Base):
    """Уведомление пользователю в кабинете. Письмо на почту уходит отдельно."""

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    expertise_id: Mapped[int | None] = mapped_column(
        ForeignKey("expertises.id", ondelete="CASCADE")
    )

    kind: Mapped[str | None] = mapped_column(String(32))
    text: Mapped[str] = mapped_column(String(500))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    expertise: Mapped[Expertise | None] = relationship()
