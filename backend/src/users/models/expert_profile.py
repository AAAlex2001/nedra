"""Профиль эксперта."""

from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class ExpertProfile(Base):
    """Квалификация эксперта."""

    __tablename__ = "expert_profiles"

    user_id: Mapped[int] = mapped_column(  # Учётная запись эксперта.
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )
    directions: Mapped[list[str]] = mapped_column(  # Направления работы эксперта.
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
    )
    audit_lead: Mapped[bool] = mapped_column(default=False)  # Право руководить аудиторской группой.
    approved_at: Mapped[datetime] = mapped_column(  # Дата одобрения эксперта.
        DateTime(timezone=True),
        server_default=func.now(),
    )
