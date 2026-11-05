"""Замечания по аудиту."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class AuditRemark(Base):
    """Замечание аудитора и ответ заказчика."""

    __tablename__ = "audit_remarks"

    id: Mapped[int] = mapped_column(primary_key=True)  # Номер замечания.
    audit_id: Mapped[int] = mapped_column(  # Заявка на аудит.
        ForeignKey(
            "audits.id",
            ondelete="CASCADE",
        ),
        index=True,
    )
    text: Mapped[str | None] = mapped_column(Text)  # Текст замечания, если оно не в файле.
    response_text: Mapped[str | None] = mapped_column(Text)  # Ответ заказчика.
    created_at: Mapped[datetime] = mapped_column(  # Дата замечания.
        DateTime(timezone=True),
        server_default=func.now(),
    )
    resolved_at: Mapped[datetime | None] = mapped_column(  # Дата устранения.
        DateTime(timezone=True)
    )
