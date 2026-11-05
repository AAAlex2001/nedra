"""Редактирование публикаций."""

from datetime import datetime
from pathlib import PurePosixPath

from pydantic import BaseModel, ConfigDict, Field

from src.articles.enums import ArticleSection
from src.articles.models.article import Article
from src.articles.models.article_content import ArticleContent
from src.articles.models.tag import Tag
from src.articles.options import DOCUMENT_KINDS, DOCUMENT_URL_PATTERN
from src.articles.schemas.article import ArticleCardResponse, ArticleResponse, TagResponse


class AdminTagResponse(TagResponse):
    """Тег редактора."""

    id: int

    @classmethod
    def from_model(cls, *, tag: Tag) -> "AdminTagResponse":
        """Подготовить тег редактора."""

        return cls(
            id=tag.id,
            slug=tag.slug,
            title=tag.title,
        )


class AdminArticleCardResponse(ArticleCardResponse):
    """Карточка редакторского списка."""

    id: int
    created_at: datetime
    updated_at: datetime
    tags: list[AdminTagResponse]

    @classmethod
    def from_model(
        cls,
        *,
        article: Article,
        tags: list[Tag],
    ) -> "AdminArticleCardResponse":
        """Подготовить карточку редактора."""

        card = ArticleCardResponse.from_model(
            article=article,
            tags=tags,
        )

        return cls(
            **card.model_dump(exclude={"tags"}),
            id=article.id,
            created_at=article.created_at,
            updated_at=article.updated_at,
            tags=[AdminTagResponse.from_model(tag=tag) for tag in tags],
        )


class AdminArticleResponse(ArticleResponse):
    """Текст и параметры редактируемой публикации."""

    id: int
    created_at: datetime
    tags: list[AdminTagResponse]

    @classmethod
    def from_article(
        cls,
        *,
        article: Article,
        content: ArticleContent,
        tags: list[Tag],
    ) -> "AdminArticleResponse":
        """Подготовить публикацию редактора."""

        page = ArticleResponse.from_article(
            article=article,
            content=content,
            tags=tags,
        )

        return cls(
            **page.model_dump(exclude={"tags"}),
            id=article.id,
            created_at=article.created_at,
            tags=[AdminTagResponse.from_model(tag=tag) for tag in tags],
        )


class AdminArticleListResponse(BaseModel):
    """Страница редакторского списка."""

    articles: list[AdminArticleCardResponse]
    total: int


class ArticleDocumentRequest(BaseModel):
    """Приложение к публикации."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    title: str = Field(
        min_length=1,
        max_length=255,
    )
    url: str = Field(pattern=DOCUMENT_URL_PATTERN)

    def to_record(self) -> dict[str, str]:
        """Подготовить приложение для хранения."""

        extension = PurePosixPath(self.url).suffix

        return {"title": self.title, "url": self.url, "kind": DOCUMENT_KINDS[extension]}


class CreateArticleRequest(BaseModel):
    """Новая публикация."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    title: str = Field(
        min_length=3,
        max_length=255,
    )
    slug: str | None = Field(
        None,
        max_length=255,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )
    section: ArticleSection = ArticleSection.BLOG
    description: str | None = Field(None, max_length=400)
    cover_image: str | None = Field(None, max_length=500)
    content: str = Field(min_length=1)
    tag_ids: list[int] = Field(default_factory=list)
    documents: list[ArticleDocumentRequest] = Field(
        default_factory=list,
        max_length=20,
    )
    published: bool = False
    published_at: datetime | None = None
    seo_title: str | None = Field(None, max_length=255)
    seo_description: str | None = Field(None, max_length=300)
    seo_keywords: str | None = Field(None, max_length=500)


class UpdateArticleRequest(BaseModel):
    """Изменения публикации."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    title: str | None = Field(
        None,
        min_length=3,
        max_length=255,
    )
    slug: str | None = Field(
        None,
        max_length=255,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )
    section: ArticleSection | None = None
    description: str | None = Field(None, max_length=400)
    cover_image: str | None = Field(None, max_length=500)
    content: str | None = Field(None, min_length=1)
    tag_ids: list[int] | None = None
    documents: list[ArticleDocumentRequest] | None = Field(None, max_length=20)
    published: bool | None = None
    published_at: datetime | None = None
    seo_title: str | None = Field(None, max_length=255)
    seo_description: str | None = Field(None, max_length=300)
    seo_keywords: str | None = Field(None, max_length=500)


class CreateTagRequest(BaseModel):
    """Новое направление публикаций."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    title: str = Field(
        min_length=2,
        max_length=100,
    )


class UploadedFileResponse(BaseModel):
    """Публичный адрес файла."""

    url: str
