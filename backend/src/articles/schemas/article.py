"""Вложенные данные публикации."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from src.articles.enums import ArticleSection
from src.articles.models.article import Article
from src.articles.models.tag import Tag


class TagResponse(BaseModel):
    """Название и адрес направления."""

    slug: str
    title: str

    @classmethod
    def from_model(cls, *, tag: Tag) -> "TagResponse":
        """Подготовить тег."""

        return cls(
            slug=tag.slug,
            title=tag.title,
        )


class ArticleCardResponse(BaseModel):
    """Карточка в списке публикаций."""

    slug: str
    section: ArticleSection
    title: str
    description: str | None
    cover_image: str | None
    published_at: datetime | None
    views_count: int
    likes_count: int
    dislikes_count: int
    tags: list[TagResponse]

    @classmethod
    def from_model(
        cls,
        *,
        article: Article,
        tags: list[Tag],
    ) -> "ArticleCardResponse":
        """Подготовить карточку."""

        return cls(
            slug=article.slug,
            section=article.section,
            title=article.title,
            description=article.description,
            cover_image=article.cover_image,
            published_at=article.published_at,
            views_count=article.views_count,
            likes_count=article.likes_count,
            dislikes_count=article.dislikes_count,
            tags=[TagResponse.from_model(tag=tag) for tag in tags],
        )


class ArticleDocumentResponse(BaseModel):
    """Документ для скачивания."""

    title: str
    url: str
    kind: Literal["pdf", "word", "excel"]
