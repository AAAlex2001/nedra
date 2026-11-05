"""Участники аудиторской группы."""

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class AuditTeamMember(Base):
    """Участник аудиторской группы."""

    __tablename__ = "audit_team_members"

    audit_id: Mapped[int] = mapped_column(  # Аудит, в группу которого входит участник.
        ForeignKey(
            "audits.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(  # Учётная запись участника группы.
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        primary_key=True,
        index=True,
    )
