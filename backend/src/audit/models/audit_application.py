"""Анкета заказчика аудита."""

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class AuditApplication(Base):
    """Сведения об объекте и объёме аудита."""

    __tablename__ = "audit_applications"

    audit_id: Mapped[int] = mapped_column(  # Аудит, для которого заполнена анкета.
        ForeignKey(
            "audits.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )
    object_name: Mapped[str | None] = mapped_column(String(500))  # Название объекта для договора.
    details: Mapped[dict | None] = mapped_column(  # Анкета; у старых заявок может отсутствовать.
        JSON().with_variant(JSONB, "postgresql"),
    )
