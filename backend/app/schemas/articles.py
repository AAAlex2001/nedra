from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Section = Literal["blog", "news"]


class TagSchema(BaseModel):
    """Тег статьи."""

    model_config = ConfigDict(from_attributes=True)

    slug: str = Field(..., description="Slug тега для фильтрации")
    title: str = Field(..., description="Название тега")


class TagAdminSchema(TagSchema):
    """Тег для админки — с идентификатором."""

    id: int = Field(..., description="ID тега")


class TagCreateSchema(BaseModel):
    """Создание тега."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(..., min_length=2, max_length=100, description="Название тега")


class ArticleCardSchema(BaseModel):
    """Схема статьи для карточки в списке всех статей."""

    model_config = ConfigDict(from_attributes=True)

    slug: str = Field(..., description="Slug статьи")
    section: Section = Field(..., description="Раздел: blog или news")
    title: str = Field(..., description="Заголовок статьи")
    description: str | None = Field(None, description="Краткое описание статьи")
    cover_image: str | None = Field(None, description="Ссылка на обложку статьи")
    published_at: datetime | None = Field(None, description="Дата публикации статьи")

    views_count: int = Field(..., description="Количество просмотров")
    likes_count: int = Field(..., description="Количество лайков")
    dislikes_count: int = Field(..., description="Количество дизлайков")

    tags: list[TagSchema] = Field(default_factory=list, description="Теги статьи")


class ArticleSeoSchema(BaseModel):
    """SEO-поля статьи. Пустые значения подменяются заголовком и описанием на фронте."""

    seo_title: str | None = Field(None, description="Заголовок для поисковика (title)")
    seo_description: str | None = Field(None, description="Meta description")
    seo_keywords: str | None = Field(None, description="Ключевые слова через запятую")


class ArticleSchema(ArticleCardSchema, ArticleSeoSchema):
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


class ArticleStatsSchema(BaseModel):
    """Счётчики статьи и реакция текущего посетителя."""

    model_config = ConfigDict(from_attributes=True)

    views_count: int = Field(..., description="Количество просмотров")
    likes_count: int = Field(..., description="Количество лайков")
    dislikes_count: int = Field(..., description="Количество дизлайков")
    my_reaction: int | None = Field(None, description="1 — лайк, -1 — дизлайк, null — нет")


class ReactionInSchema(BaseModel):
    """Реакция посетителя."""

    model_config = ConfigDict(extra="forbid")

    value: Literal[1, -1] = Field(..., description="1 — лайк, -1 — дизлайк")


class ArticleAdminCardSchema(ArticleCardSchema):
    """Статья в списке админки."""

    id: int = Field(..., description="ID статьи")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата последнего изменения")
    tags: list[TagAdminSchema] = Field(default_factory=list, description="Теги статьи")


class ArticleAdminSchema(ArticleAdminCardSchema, ArticleSeoSchema):
    """Статья целиком для редактирования."""

    content: str = Field(..., description="HTML-контент статьи")
    toc: list[dict[str, str]] = Field(default_factory=list, description="Оглавление")


class ArticleCreateSchema(BaseModel):
    """Создание статьи."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(..., min_length=3, max_length=255, description="Заголовок")
    slug: str | None = Field(
        None, max_length=255, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        description="Slug; если не задан — строится из заголовка",
    )
    section: Section = Field("blog", description="Раздел: blog или news")
    description: str | None = Field(None, max_length=400, description="Краткое описание")
    cover_image: str | None = Field(None, max_length=500, description="Путь к обложке")
    content: str = Field(..., min_length=1, description="HTML-контент")
    tag_ids: list[int] = Field(default_factory=list, description="ID тегов")
    published: bool = Field(False, description="Опубликовать сразу")
    published_at: datetime | None = Field(
        None,
        description="Дата публикации. Если в будущем — статья выйдет сама в этот момент",
    )
    seo_title: str | None = Field(None, max_length=255, description="Title для поисковика")
    seo_description: str | None = Field(None, max_length=300, description="Meta description")
    seo_keywords: str | None = Field(None, max_length=500, description="Ключевые слова")


class ArticleUpdateSchema(BaseModel):
    """Частичное обновление статьи."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str | None = Field(None, min_length=3, max_length=255)
    slug: str | None = Field(None, max_length=255, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    section: Section | None = None
    description: str | None = Field(None, max_length=400)
    cover_image: str | None = Field(None, max_length=500)
    content: str | None = Field(None, min_length=1)
    tag_ids: list[int] | None = None
    published: bool | None = None
    published_at: datetime | None = None
    seo_title: str | None = Field(None, max_length=255)
    seo_description: str | None = Field(None, max_length=300)
    seo_keywords: str | None = Field(None, max_length=500)


class UploadResultSchema(BaseModel):
    """Результат загрузки файла."""

    url: str = Field(..., description="Публичный путь к файлу")
