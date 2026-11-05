"""Направления публикаций."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class Tag(Base):
    """Тег для поиска статей."""

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)  # Номер тега.
    slug: Mapped[str] = mapped_column(String(100), unique=True)  # Адрес фильтра.
    title: Mapped[str] = mapped_column(String(100))  # Название направления.
