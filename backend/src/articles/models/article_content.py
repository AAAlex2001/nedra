"""Текст и поисковое описание статьи."""

from sqlalchemy import JSON, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class ArticleContent(Base):
    """Содержимое страницы публикации."""

    __tablename__ = "article_contents"

    article_id: Mapped[int] = mapped_column(  # Публикация.
        ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True
    )
    content: Mapped[str] = mapped_column(Text)  # Очищенный HTML.
    toc: Mapped[list[dict[str, str]]] = mapped_column(  # Оглавление.
        JSON().with_variant(JSONB, "postgresql"), default=list
    )
    documents: Mapped[list[dict[str, str]]] = mapped_column(  # Приложенные документы.
        JSON().with_variant(JSONB, "postgresql"),
        default=list,
        server_default=text("'[]'"),
    )
    seo_title: Mapped[str | None] = mapped_column(String(255))  # Заголовок для поисковика.
    seo_description: Mapped[str | None] = mapped_column(String(300))  # Поисковое описание.
    seo_keywords: Mapped[str | None] = mapped_column(String(500))  # Ключевые слова.
