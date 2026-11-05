"""Условия и этапы экспертизы."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base
from src.expertise.enums import ExpertiseStatus


class Expertise(Base):
    """Экспертиза промышленной безопасности."""

    __tablename__ = "expertises"

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
    expert_id: Mapped[int | None] = mapped_column(  # Назначенный эксперт.
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        index=True,
    )
    status: Mapped[str] = mapped_column(  # Текущий этап экспертизы.
        String(32),
        default=ExpertiseStatus.NEW,
        index=True,
    )
    object_name: Mapped[str | None] = mapped_column(String(500))  # Наименование документации.
    object_code: Mapped[str | None] = mapped_column(  # Код объекта экспертизы.
        String(8),
        index=True,
    )
    area_code: Mapped[str | None] = mapped_column(  # Область аттестации эксперта.
        String(8),
        index=True,
    )
    hazard_class: Mapped[int | None] = mapped_column(SmallInteger)  # Класс опасности ОПО.
    expert_category: Mapped[int | None] = mapped_column(  # Требуемая категория эксперта.
        SmallInteger
    )
    deadline: Mapped[str | None] = mapped_column(String(16))  # Желаемый срок выполнения.
    price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))  # Стоимость в рублях.
    result: Mapped[str | None] = mapped_column(  # Положительное или отрицательное заключение.
        String(16)
    )
    expert_ready_at: Mapped[datetime | None] = (  # Дата согласия эксперта выполнить работу.
        mapped_column(
            DateTime(timezone=True),
        )
    )
    conclusion_ready_at: Mapped[datetime | None] = mapped_column(  # Дата готовности заключения.
        DateTime(timezone=True),
    )
    sent_at: Mapped[datetime | None] = mapped_column(  # Дата отправки заключения.
        DateTime(timezone=True),
    )
    accepted_at: Mapped[datetime | None] = mapped_column(  # Дата приёмки работы.
        DateTime(timezone=True),
    )
