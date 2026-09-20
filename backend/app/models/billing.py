from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class InvoiceStage(StrEnum):
    """Этап оплаты, за который выставлен счёт."""

    ADVANCE = "advance"
    FINAL = "final"


class CustomerCompany(Base):
    """Реквизиты организации заказчика. Печатаются в счёте и акте."""

    __tablename__ = "customer_companies"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )

    name: Mapped[str] = mapped_column(String(255))
    inn: Mapped[str] = mapped_column(String(12))
    kpp: Mapped[str | None] = mapped_column(String(9))
    address: Mapped[str] = mapped_column(String(500))

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Invoice(Base):
    """Счёт на оплату этапа экспертизы для юридического лица.

    Реквизиты плательщика копируются в счёт при выставлении: выставленный
    документ не должен меняться, если заказчик потом поправит профиль.
    Оплату подтверждает администратор, когда деньги пришли на счёт.
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
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
