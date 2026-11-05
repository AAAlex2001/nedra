"""Похожие публикации."""

from datetime import datetime

from pydantic import BaseModel, Field
from src.articles.enums import ArticleSection
from src.articles.models.article import Article
from src.articles.models.tag import Tag
from src.articles.schemas.article import TagResponse


class RelatedArticlesRequest(BaseModel):
    """Публикация и размер подборки."""

    slug: str
    limit: int = Field(default=10, ge=1, le=20)


class RelatedArticleResponse(BaseModel):
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
    ) -> "RelatedArticleResponse":
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
