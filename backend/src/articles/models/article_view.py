"""Уникальные просмотры."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class ArticleView(Base):
    """Просмотр статьи посетителем."""

    __tablename__ = "article_views"

    article_id: Mapped[int] = mapped_column(  # Публикация.
        ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True
    )
    visitor_id: Mapped[str] = mapped_column(String(36), primary_key=True)  # Посетитель из cookie.
    created_at: Mapped[datetime] = mapped_column(  # Первый просмотр.
        DateTime(timezone=True), server_default=func.now()
    )
