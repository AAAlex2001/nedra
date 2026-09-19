from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Tariff(Base):
    """Стоимость экспертизы для пары «область аттестации × объект экспертизы».

    Задаёт админ. Когда эксперт берёт заявку, цена подставляется отсюда,
    поэтому у пары может быть только одна запись.
    """

    __tablename__ = "tariffs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    area_code: Mapped[str] = mapped_column(String(8))
    object_code: Mapped[str] = mapped_column(String(8))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        UniqueConstraint("area_code", "object_code", name="uq_tariffs_area_object"),
    )
