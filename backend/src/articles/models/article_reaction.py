"""Реакции посетителей."""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class ArticleReaction(Base):
    """Одна реакция посетителя на статью."""

    __tablename__ = "article_reactions"
    __table_args__ = (CheckConstraint("value IN (-1, 1)", name="ck_article_reactions_value"),)

    article_id: Mapped[int] = mapped_column(  # Публикация.
        ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True
    )
    visitor_id: Mapped[str] = mapped_column(String(36), primary_key=True)  # Посетитель из cookie.
    value: Mapped[int] = mapped_column(SmallInteger)  # 1 — нравится, -1 — не нравится.
    created_at: Mapped[datetime] = mapped_column(  # Дата реакции.
        DateTime(timezone=True), server_default=func.now()
    )
