"""Теги выбранной публикации."""

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class ArticleTag(Base):
    """Привязка тега к статье."""

    __tablename__ = "article_tags"

    article_id: Mapped[int] = mapped_column(  # Публикация.
        ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[int] = mapped_column(  # Тег.
        ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    )
