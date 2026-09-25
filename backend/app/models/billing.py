from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.expertise import Expertise


class InvoiceStage(StrEnum):
    """Этап оплаты, за который выставлен счёт."""

    ADVANCE = "advance"
    FINAL = "final"


class Invoice(Base):
    """Счёт на оплату этапа экспертизы для юридического лица.

    Реквизиты плательщика копируются в счёт из заявки при выставлении:
    выставленный документ не должен меняться. Оплату подтверждает
    администратор, когда деньги пришли на счёт.
    """

    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    expertise_id: Mapped[int] = mapped_column(
        ForeignKey("expertises.id", ondelete="CASCADE"), index=True
    )

    stage: Mapped[str] = mapped_column(String(16))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    payer_name: Mapped[str] = mapped_column(String(255))
    payer_inn: Mapped[str] = mapped_column(String(12))
    payer_kpp: Mapped[str | None] = mapped_column(String(9))
    payer_address: Mapped[str] = mapped_column(String(500))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    reported_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    expertise: Mapped["Expertise"] = relationship(back_populates="invoices")
