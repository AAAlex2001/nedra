"""Список направлений."""

from pydantic import BaseModel
from src.articles.enums import ArticleSection
from src.articles.models.tag import Tag


class ListTagsRequest(BaseModel):
    """Раздел публикаций."""

    section: ArticleSection | None = None


class ListedTagResponse(BaseModel):
    """Название и адрес направления."""

    slug: str
    title: str

    @classmethod
    def from_model(cls, *, tag: Tag) -> "ListedTagResponse":
        """Подготовить тег."""

        return cls(
            slug=tag.slug,
            title=tag.title,
        )
