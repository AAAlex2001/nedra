"""Платежи через платёжную систему."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class Payment(Base):
    """Платёж пользователя."""

    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)  # Номер платежа.
    user_id: Mapped[int] = mapped_column(  # Плательщик.
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        index=True,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))  # Сумма платежа.
    currency: Mapped[str] = mapped_column(  # Код валюты.
        String(3),
        default="RUB",
    )
    description: Mapped[str] = mapped_column(String(128))  # Назначение платежа.
    status: Mapped[str] = mapped_column(  # Статус у провайдера.
        String(32),
        index=True,
    )
    provider_payment_id: Mapped[str] = mapped_column(  # Номер у провайдера.
        String(64),
        unique=True,
        index=True,
    )
    confirmation_url: Mapped[str | None] = mapped_column(String(1024))  # Ссылка для оплаты.
    created_at: Mapped[datetime] = mapped_column(  # Дата создания.
        DateTime(timezone=True),
        server_default=func.now(),
    )
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))  # Дата оплаты.
