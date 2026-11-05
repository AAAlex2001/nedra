"""Публикации на сайте."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from src.articles.enums import ArticleSection
from src.articles.models.article import Article
from src.articles.models.article_content import ArticleContent
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


class ArticleResponse(ArticleCardResponse):
    """Страница публикации."""

    content: str
    toc: list[dict[str, str]]
    documents: list[ArticleDocumentResponse]
    seo_title: str | None
    seo_description: str | None
    seo_keywords: str | None
    updated_at: datetime

    @classmethod
    def from_article(
        cls,
        *,
        article: Article,
        content: ArticleContent,
        tags: list[Tag],
    ) -> "ArticleResponse":
        """Подготовить страницу."""

        card = ArticleCardResponse.from_model(
            article=article,
            tags=tags,
        )

        return cls(
            **card.model_dump(),
            content=content.content,
            toc=content.toc,
            documents=content.documents,
            seo_title=content.seo_title,
            seo_description=content.seo_description,
            seo_keywords=content.seo_keywords,
            updated_at=article.updated_at,
        )


class ArticleListResponse(BaseModel):
    """Страница списка публикаций."""

    articles: list[ArticleCardResponse]
    total: int
