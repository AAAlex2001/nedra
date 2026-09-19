from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class PaymentStatus(StrEnum):
    """Статусы платежа. Совпадают со статусами ЮKassa, чтобы не переводить туда-обратно."""

    PENDING = "pending"
    WAITING_FOR_CAPTURE = "waiting_for_capture"
    SUCCEEDED = "succeeded"
    CANCELED = "canceled"


class Payment(Base):
    """Платёж пользователя через ЮKassa.

    Сумму и назначение задаёт сервер, а не клиент. Другие модули
    (например, экспертиза) хранят ссылку на платёж и по его статусу
    решают, можно ли двигаться дальше.
    """

    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True)

    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    currency: Mapped[str] = mapped_column(String(3), default="RUB")
    description: Mapped[str] = mapped_column(String(128))

    status: Mapped[str] = mapped_column(String(32), index=True)

    provider_payment_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    confirmation_url: Mapped[str | None] = mapped_column(String(1024))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
