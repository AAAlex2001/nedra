"""Список публикаций."""

from pydantic import BaseModel, Field

from src.articles.enums import ArticleSection, ArticleSort
from src.articles.schemas.article import ArticleCardResponse


class ListArticlesRequest(BaseModel):
    """Фильтры и сортировка."""

    section: ArticleSection | None = None
    tag: str | None = None
    search: str | None = Field(default=None, max_length=100)
    sort: ArticleSort = ArticleSort.NEWEST
    limit: int = Field(default=12, ge=1, le=50)
    offset: int = Field(default=0, ge=0)


class ListArticlesResponse(BaseModel):
    """Страница списка публикаций."""

    articles: list[ArticleCardResponse]
    total: int
