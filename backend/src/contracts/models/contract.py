"""Договоры по заявкам."""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class Contract(Base):
    """Условия договора по заявке."""

    __tablename__ = "contracts"
    __table_args__ = (
        CheckConstraint("num_nonnulls(expertise_id, audit_id) = 1", name="ck_contract_service"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)  # Номер договора.
    expertise_id: Mapped[int | None] = mapped_column(  # Экспертиза.
        ForeignKey("expertises.id", ondelete="CASCADE"),
        unique=True,
    )
    audit_id: Mapped[int | None] = mapped_column(  # Аудит.
        ForeignKey("audits.id", ondelete="CASCADE"),
        unique=True,
    )

    kind: Mapped[str | None] = mapped_column(String(16))  # Вид договора.
    confirmed_at: Mapped[datetime | None] = mapped_column(  # Дата подтверждения.
        DateTime(timezone=True)
    )
