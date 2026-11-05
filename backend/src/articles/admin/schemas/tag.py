"""Создание и просмотр тегов."""

from pydantic import BaseModel, ConfigDict, Field
from src.articles.models.tag import Tag


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


class AdminTagResponse(BaseModel):
    """Тег редактора."""

    id: int
    slug: str
    title: str

    @classmethod
    def from_model(cls, *, tag: Tag) -> "AdminTagResponse":
        """Подготовить тег редактора."""

        return cls(
            id=tag.id,
            slug=tag.slug,
            title=tag.title,
        )
