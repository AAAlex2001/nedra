"""Замечания по экспертизе."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class ExpertiseRemark(Base):
    """Замечание эксперта и ответ заказчика."""

    __tablename__ = "expertise_remarks"

    id: Mapped[int] = mapped_column(primary_key=True)  # Номер замечания.
    expertise_id: Mapped[int] = mapped_column(  # Заявка на экспертизу.
        ForeignKey(
            "expertises.id",
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
