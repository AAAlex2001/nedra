"""Данные заказчика-физлица."""

from datetime import date

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class ExpertiseIndividual(Base):
    """Паспортные данные заказчика экспертизы."""

    __tablename__ = "expertise_individuals"

    expertise_id: Mapped[int] = mapped_column(  # Номер экспертизы.
        ForeignKey("expertises.id", ondelete="CASCADE"),
        primary_key=True,
    )
    full_name: Mapped[str] = mapped_column(String(255))  # ФИО заказчика.
    passport_number: Mapped[str] = mapped_column(String(20))  # Серия и номер паспорта.
    passport_issued_by: Mapped[str] = mapped_column(String(500))  # Орган выдачи.
    passport_issued_at: Mapped[date]  # Дата выдачи.
    address: Mapped[str] = mapped_column(String(500))  # Адрес регистрации.
