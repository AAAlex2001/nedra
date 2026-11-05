"""Тариф на услугу."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class Tariff(Base):
    """Цена по области и объекту экспертизы."""

    __tablename__ = "tariffs"
    __table_args__ = (
        UniqueConstraint(
            "area_code",
            "object_code",
            name="uq_tariffs_area_object",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)  # Номер тарифа.
    area_code: Mapped[str] = mapped_column(String(8))  # Код области аттестации.
    object_code: Mapped[str] = mapped_column(String(8))  # Код объекта экспертизы.
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))  # Стоимость в рублях.
    updated_at: Mapped[datetime] = mapped_column(  # Дата изменения цены.
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
