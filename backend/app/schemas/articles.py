from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TagSchema(BaseModel):
    """Тег статьи."""

    model_config = ConfigDict(from_attributes=True)

    slug: str = Field(..., description="Slug тега для фильтрации")
    title: str = Field(..., description="Название тега")


class ArticleCardSchema(BaseModel):
    """Схема статьи для карточки в списке всех статей."""

    model_config = ConfigDict(from_attributes=True)

    slug: str = Field(..., description="Slug статьи")
    title: str = Field(..., description="Заголовок статьи")
    description: str | None = Field(None, description="Краткое описание статьи")
    cover_image: str | None = Field(None, description="Ссылка на обложку статьи")
    published_at: datetime | None = Field(None, description="Дата публикации статьи")

    views_count: int = Field(..., description="Количество просмотров")
    likes_count: int = Field(..., description="Количество лайков")
    dislikes_count: int = Field(..., description="Количество дизлайков")

    tags: list[TagSchema] = Field(default_factory=list, description="Теги статьи")


class ArticleSchema(ArticleCardSchema):
    """Схема статьи для страницы статьи."""

    content: str = Field(..., description="HTML-контент статьи")
    toc: list[dict[str, str]] = Field(
        default_factory=list, description="Оглавление из заголовков H2"
    )


class ArticleListSchema(BaseModel):
    """Схема списка статей с пагинацией."""

    articles: list[ArticleCardSchema] = Field(
        ..., description="Статьи на текущей странице"
    )
    total: int = Field(..., description="Общее количество статей с учётом фильтра")
