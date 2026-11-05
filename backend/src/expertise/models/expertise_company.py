"""Реквизиты заказчика."""

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class ExpertiseCompany(Base):
    """Реквизиты организации по заявке."""

    __tablename__ = "expertise_companies"

    expertise_id: Mapped[int] = mapped_column(  # Номер заявки.
        ForeignKey("expertises.id", ondelete="CASCADE"),
        primary_key=True,
    )
    full_name: Mapped[str] = mapped_column(String(500))  # Полное наименование.
    name: Mapped[str] = mapped_column(String(255))  # Сокращённое наименование.
    inn: Mapped[str] = mapped_column(String(12))  # ИНН.
    kpp: Mapped[str | None] = mapped_column(String(9))  # КПП.
    ogrn: Mapped[str] = mapped_column(String(15))  # ОГРН или ОГРНИП.
    address: Mapped[str] = mapped_column(String(500))  # Юридический адрес.
    bank: Mapped[str] = mapped_column(String(255))  # Банк.
    bic: Mapped[str] = mapped_column(String(9))  # БИК банка.
    account: Mapped[str] = mapped_column(String(20))  # Расчётный счёт.
    corr_account: Mapped[str] = mapped_column(String(20))  # Корреспондентский счёт.
    signer_position: Mapped[str] = mapped_column(String(255))  # Должность подписанта.
    signer_name: Mapped[str] = mapped_column(String(255))  # ФИО подписанта.
    signer_genitive: Mapped[str] = mapped_column(String(500))  # Подписант в родительном падеже.
    signer_basis: Mapped[str] = mapped_column(String(255))  # Основание полномочий.
