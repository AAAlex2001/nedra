"""Просмотр публикации редактором."""

from datetime import datetime

from pydantic import BaseModel

from src.articles.admin.schemas.tag import AdminTagResponse
from src.articles.enums import ArticleSection
from src.articles.models.article import Article
from src.articles.models.article_content import ArticleContent
from src.articles.models.tag import Tag
from src.articles.schemas.article import ArticleDocumentResponse


class GetArticleRequest(BaseModel):
    """Номер публикации."""

    article_id: int


class GetArticleResponse(BaseModel):
    """Публикация для редактирования."""

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
    content: str
    toc: list[dict[str, str]]
    documents: list[ArticleDocumentResponse]
    seo_title: str | None
    seo_description: str | None
    seo_keywords: str | None

    @classmethod
    def from_model(
        cls,
        *,
        article: Article,
        content: ArticleContent,
        tags: list[Tag],
    ) -> "GetArticleResponse":
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
            content=content.content,
            toc=content.toc,
            documents=content.documents,
            seo_title=content.seo_title,
            seo_description=content.seo_description,
            seo_keywords=content.seo_keywords,
        )
