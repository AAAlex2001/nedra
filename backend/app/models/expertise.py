from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ExpertiseStatus(StrEnum):
    """Путь экспертизы от подачи документации до приёмки работы.

    new — заявка подана, ждёт эксперта;
    expert_ready — эксперт готов провести экспертизу, ждём согласия заказчика;
    contract — обе стороны согласились, договор считается заключённым, ждём аванс;
    in_progress — аванс оплачен, эксперт работает;
    conclusion_ready — эксперт сообщил, что заключение готово, ждём остаток;
    paid — остаток оплачен, эксперт подписывает заключение и отправляет;
    sent — заключение отправлено заказчику;
    accepted — заказчик принял работу.
    """

    NEW = "new"
    EXPERT_READY = "expert_ready"
    CONTRACT = "contract"
    IN_PROGRESS = "in_progress"
    CONCLUSION_READY = "conclusion_ready"
    PAID = "paid"
    SENT = "sent"
    ACCEPTED = "accepted"


class ExpertiseResult(StrEnum):
    """Исход экспертизы, который эксперт указывает при отправке заключения."""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    REMARKS = "remarks"


class Expertise(Base):
    """Заявка заказчика на экспертизу промышленной безопасности.

    Заказчик указывает объект экспертизы, область аттестации и класс опасности
    объекта или требуемую категорию эксперта, прикладывает документацию.
    Цена берётся из тарифа в момент подачи, чтобы смена тарифа не меняла
    уже поданные заявки. Эксперт назначается позже, поэтому expert_id пустой.
    """

    __tablename__ = "expertises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True
    )
    expert_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )

    object_code: Mapped[str] = mapped_column(String(8), index=True)
    area_code: Mapped[str] = mapped_column(String(8), index=True)
    hazard_class: Mapped[int | None] = mapped_column(SmallInteger)
    expert_category: Mapped[int] = mapped_column(SmallInteger)

    comment: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), index=True, default=ExpertiseStatus.NEW)
    price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    result: Mapped[str | None] = mapped_column(String(16))

    advance_payment_id: Mapped[int | None] = mapped_column(
        ForeignKey("payments.id", ondelete="SET NULL")
    )
    final_payment_id: Mapped[int | None] = mapped_column(
        ForeignKey("payments.id", ondelete="SET NULL")
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expert_ready_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    contract_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    advance_paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    conclusion_ready_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    final_paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    documents: Mapped[list["ExpertiseDocument"]] = relationship(
        back_populates="expertise",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="ExpertiseDocument.id",
    )


class ExpertiseDocument(Base):
    """Файл, приложенный к экспертизе: документация заказчика или заключение эксперта."""

    __tablename__ = "expertise_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    expertise_id: Mapped[int] = mapped_column(
        ForeignKey("expertises.id", ondelete="CASCADE"), index=True
    )
    uploaded_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))

    kind: Mapped[str] = mapped_column(String(32), default="documentation")
    file_path: Mapped[str] = mapped_column(String(500))
    original_name: Mapped[str] = mapped_column(String(255))
    size: Mapped[int] = mapped_column(Integer)
    content_type: Mapped[str] = mapped_column(String(128))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    expertise: Mapped["Expertise"] = relationship(back_populates="documents")
