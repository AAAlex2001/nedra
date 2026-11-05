"""Условия и этапы аудита."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.audit.enums import AuditStatus
from src.core.database import Base


class Audit(Base):
    """Аудит системы управления промышленной безопасностью."""

    __tablename__ = "audits"

    id: Mapped[int] = mapped_column(primary_key=True)  # Номер заявки.
    customer_id: Mapped[int] = mapped_column(  # Заказчик.
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
    )
    customer_type: Mapped[str] = mapped_column(String(16), default="legal")  # Вид заказчика.
    comment: Mapped[str | None] = mapped_column(Text)  # Комментарий заказчика.
    created_at: Mapped[datetime] = mapped_column(  # Дата подачи.
        DateTime(timezone=True),
        server_default=func.now(),
    )
    lead_id: Mapped[int | None] = mapped_column(  # Руководитель аудиторской группы.
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        index=True,
    )
    status: Mapped[str] = mapped_column(  # Текущий этап аудита.
        String(32),
        default=AuditStatus.NEW,
        index=True,
    )
    customer_budget: Mapped[Decimal | None] = mapped_column(  # Исходный бюджет в рублях.
        Numeric(10, 2)
    )
    negotiation_allowed: Mapped[bool] = mapped_column(  # Готовность заказчика обсуждать цену.
        default=True
    )
    offer_price: Mapped[Decimal | None] = mapped_column(  # Цена, предложенная аудитором.
        Numeric(10, 2)
    )
    counter_price: Mapped[Decimal | None] = mapped_column(  # Встречная цена заказчика.
        Numeric(10, 2)
    )
    agreed_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))  # Согласованная стоимость.
    result: Mapped[str | None] = mapped_column(  # Положительный или отрицательный результат.
        String(16)
    )
    lead_ready_at: Mapped[datetime | None] = (  # Дата согласия руководителя провести аудит.
        mapped_column(
            DateTime(timezone=True),
        )
    )
    conclusion_ready_at: Mapped[datetime | None] = (  # Дата готовности итогового документа.
        mapped_column(
            DateTime(timezone=True),
        )
    )
    sent_at: Mapped[datetime | None] = mapped_column(  # Дата отправки результата заказчику.
        DateTime(timezone=True),
    )
    accepted_at: Mapped[datetime | None] = mapped_column(  # Дата приёмки работы заказчиком.
        DateTime(timezone=True),
    )
