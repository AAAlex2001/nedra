"""Список публикаций редактора."""

from datetime import datetime

from pydantic import BaseModel, Field
from src.articles.admin.schemas.tag import AdminTagResponse
from src.articles.enums import AdminArticleSort, ArticleSection
from src.articles.models.article import Article
from src.articles.models.tag import Tag


class ArticleListItem(BaseModel):
    """Публикация в списке."""

    id: int
    slug: str
    section: ArticleSection
    title: str
    description: str | None
    cover_image: str | None
    published_at: datetime | None
    views_count: int
    likes_count: int
    dislikes_count: int
    created_at: datetime
    updated_at: datetime
    tags: list[AdminTagResponse]

    @classmethod
    def from_model(cls, *, article: Article, tags: list[Tag]) -> "ArticleListItem":
        """Подготовить ответ."""

        return cls(
            id=article.id,
            slug=article.slug,
            section=article.section,
            title=article.title,
            description=article.description,
            cover_image=article.cover_image,
            published_at=article.published_at,
            views_count=article.views_count,
            likes_count=article.likes_count,
            dislikes_count=article.dislikes_count,
            created_at=article.created_at,
            updated_at=article.updated_at,
            tags=[AdminTagResponse.from_model(tag=tag) for tag in tags],
        )


class ListArticlesRequest(BaseModel):
    """Фильтры и страница списка."""

    section: ArticleSection | None = None
    sort: AdminArticleSort = AdminArticleSort.NEW
    q: str | None = Field(default=None, max_length=100)
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class ListArticlesResponse(BaseModel):
    """Найденные публикации."""

    articles: list[ArticleListItem]
    total: int
