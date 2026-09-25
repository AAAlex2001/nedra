from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import JSON, Date, DateTime, ForeignKey, Integer, SmallInteger, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ApplicationStatus(StrEnum):
    """Статус заявки эксперта на регистрацию."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ExpertApplication(Base):
    """Заявка эксперта на регистрацию.

    Эксперт не регистрируется сам: он подаёт заявку с удостоверениями,
    админ проверяет и одобряет. Только после этого создаётся пользователь
    с ролью expert, а хеш пароля переносится из заявки.
    """

    __tablename__ = "expert_applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    email: Mapped[str] = mapped_column(String(320), index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(32))

    directions: Mapped[list[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), default=list
    )

    status: Mapped[str] = mapped_column(String(16), index=True, default=ApplicationStatus.PENDING)
    admin_comment: Mapped[str | None] = mapped_column(String(1000))

    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    certificates: Mapped[list["ExpertCertificate"]] = relationship(
        back_populates="application",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="ExpertCertificate.id",
    )


class ExpertCertificate(Base):
    """Удостоверение эксперта: область аттестации, объект экспертизы, категория.

    Сначала принадлежит заявке. После одобрения получает user_id
    и становится удостоверением зарегистрированного эксперта.
    Эксперт указывает номер удостоверения или номер регистрации в ЕРУЛ.
    Сканы больше не принимаются, поля скана остались у старых заявок.
    """

    __tablename__ = "expert_certificates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    application_id: Mapped[int | None] = mapped_column(
        ForeignKey("expert_applications.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )

    area_code: Mapped[str] = mapped_column(String(8))
    object_code: Mapped[str] = mapped_column(String(8))
    category: Mapped[int] = mapped_column(SmallInteger)
    valid_until: Mapped[date] = mapped_column(Date)
    number: Mapped[str | None] = mapped_column(String(64))

    scan_path: Mapped[str | None] = mapped_column(String(500))
    scan_name: Mapped[str | None] = mapped_column(String(255))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    application: Mapped["ExpertApplication | None"] = relationship(
        back_populates="certificates"
    )


class ExpertProfile(Base):
    """Профиль одобренного эксперта: направления работы и дата одобрения."""

    __tablename__ = "expert_profiles"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )

    directions: Mapped[list[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), default=list
    )

    approved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
