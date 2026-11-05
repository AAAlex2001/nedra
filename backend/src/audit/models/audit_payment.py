"""Оплата этапов заявки."""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class AuditPayment(Base):
    """Оплата аванса или окончательного расчёта."""

    __tablename__ = "audit_payments"
    __table_args__ = (
        CheckConstraint(
            "stage IN ('advance', 'final')",
            name="ck_audit_payments_stage",
        ),
    )

    audit_id: Mapped[int] = mapped_column(  # Оплачиваемая заявка.
        ForeignKey(
            "audits.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )
    stage: Mapped[str] = mapped_column(  # Аванс или окончательный расчёт.
        String(16),
        primary_key=True,
    )
    payment_id: Mapped[int | None] = mapped_column(  # Платёж через платёжную систему.
        ForeignKey(
            "payments.id",
            ondelete="SET NULL",
        ),
        index=True,
    )
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))  # Дата оплаты этапа.
