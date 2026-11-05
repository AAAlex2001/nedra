"""Документы заявки."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class ExpertiseDocument(Base):
    """Загруженный документ."""

    __tablename__ = "expertise_documents"

    id: Mapped[int] = mapped_column(primary_key=True)  # Номер документа.
    expertise_id: Mapped[int] = mapped_column(  # Номер заявки.
        ForeignKey("expertises.id", ondelete="CASCADE"),
        index=True,
    )
    remark_id: Mapped[int | None] = mapped_column(  # Замечание к документу.
        ForeignKey("expertise_remarks.id", ondelete="CASCADE"),
        index=True,
    )
    uploaded_by: Mapped[int | None] = mapped_column(  # Автор загрузки.
        ForeignKey("users.id", ondelete="SET NULL"),
    )
    kind: Mapped[str] = mapped_column(String(32))  # Назначение документа.
    item_number: Mapped[int | None] = mapped_column(SmallInteger)  # Номер пункта перечня.
    file_path: Mapped[str] = mapped_column(String(500))  # Путь в закрытом хранилище.
    original_name: Mapped[str] = mapped_column(String(255))  # Исходное имя файла.
    size: Mapped[int]  # Размер в байтах.
    content_type: Mapped[str] = mapped_column(String(128))  # MIME-тип файла.
    created_at: Mapped[datetime] = mapped_column(  # Дата загрузки.
        DateTime(timezone=True),
        server_default=func.now(),
    )
