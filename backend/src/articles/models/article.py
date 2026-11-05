"""Публикации новостей и блога."""

from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class Article(Base):
    """Карточка публикации."""

    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)  # Номер публикации.
    slug: Mapped[str] = mapped_column(String(255), unique=True)  # Адрес публикации.
    section: Mapped[str] = mapped_column(  # Раздел сайта.
        String(16),
        default="blog",
        server_default="blog",
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255))  # Заголовок.
    description: Mapped[str | None] = mapped_column(String(400))  # Краткое описание.
    cover_image: Mapped[str | None] = mapped_column(String(500))  # Обложка.
    views_count: Mapped[int] = mapped_column(default=0)  # Уникальные просмотры.
    likes_count: Mapped[int] = mapped_column(default=0)  # Положительные реакции.
    dislikes_count: Mapped[int] = mapped_column(default=0)  # Отрицательные реакции.
    published_at: Mapped[datetime | None] = mapped_column(  # Дата публикации.
        DateTime(timezone=True), index=True
    )
    created_at: Mapped[datetime] = mapped_column(  # Дата создания.
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(  # Дата редактирования.
        DateTime(timezone=True), server_default=func.now()
    )
