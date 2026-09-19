from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, Integer, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ExpertiseStatus(StrEnum):
    """Статусы экспертизы. Пока только подача, остальные шаги добавим по мере реализации."""

    NEW = "new"


class Expertise(Base):
    """Заявка заказчика на экспертизу промышленной безопасности.

    Заказчик указывает объект экспертизы, область аттестации и класс опасности
    объекта или требуемую категорию эксперта, прикладывает документацию.
    Эксперт назначается позже, поэтому expert_id пустой при создании.
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

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    documents: Mapped[list["ExpertiseDocument"]] = relationship(
        back_populates="expertise",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="ExpertiseDocument.id",
    )


class ExpertiseDocument(Base):
    """Файл, приложенный к экспертизе: документация заказчика, позже договоры и заключение."""

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
