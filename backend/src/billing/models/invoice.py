"""Счета для безналичной оплаты."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class Invoice(Base):
    """Выставленный счёт с реквизитами плательщика."""

    __tablename__ = "invoices"
    __table_args__ = (
        CheckConstraint("num_nonnulls(expertise_id, audit_id) = 1", name="ck_invoice_service"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)  # Номер счёта.
    expertise_id: Mapped[int | None] = mapped_column(  # Экспертиза.
        ForeignKey("expertises.id", ondelete="CASCADE"),
        index=True,
    )
    audit_id: Mapped[int | None] = mapped_column(  # Аудит.
        ForeignKey("audits.id", ondelete="CASCADE"),
        index=True,
    )

    stage: Mapped[str] = mapped_column(String(16))  # Этап оплаты.
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))  # Сумма в рублях.
    payer_name: Mapped[str] = mapped_column(String(255))  # Наименование плательщика.
    payer_inn: Mapped[str] = mapped_column(String(12))  # ИНН плательщика.
    payer_kpp: Mapped[str | None] = mapped_column(String(9))  # КПП плательщика.
    payer_address: Mapped[str] = mapped_column(String(500))  # Адрес плательщика.
    created_at: Mapped[datetime] = mapped_column(  # Дата выставления.
        DateTime(timezone=True),
        server_default=func.now(),
    )
    reported_at: Mapped[datetime | None] = mapped_column(  # Дата сообщения об оплате.
        DateTime(timezone=True)
    )
    paid_at: Mapped[datetime | None] = mapped_column(  # Дата подтверждения оплаты.
        DateTime(timezone=True)
    )
