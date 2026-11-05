"""План проведения аудита."""

from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class AuditPlan(Base):
    """План аудита и его согласование."""

    __tablename__ = "audit_plans"

    audit_id: Mapped[int] = mapped_column(  # Аудит, для которого подготовлен план.
        ForeignKey(
            "audits.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )
    plan: Mapped[dict | None] = mapped_column(  # Последняя версия плана.
        JSON().with_variant(JSONB, "postgresql"),
    )
    comment: Mapped[str | None] = mapped_column(Text)  # Просьба заказчика скорректировать план.
    sent_at: Mapped[datetime | None] = mapped_column(  # Дата отправки плана на согласование.
        DateTime(timezone=True),
    )
    approved_at: Mapped[datetime | None] = mapped_column(  # Дата согласования плана.
        DateTime(timezone=True),
    )
