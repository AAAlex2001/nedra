"""Сценарий создания тега."""

from app.models.article import Tag
from app.services.articles.content import make_slug
from app.services.articles.tags import TagRepository


class CreateTagUseCase:
    """Построить slug из названия и сохранить тег."""

    def __init__(self, tags: TagRepository) -> None:
        self.tags = tags

    async def execute(self, title: str) -> Tag:
        """Создать тег. При совпадении slug получает суффикс."""

        wanted_slug = make_slug(title, max_length=90)
        slug = await self.tags.unique_slug(wanted_slug)

        tag = Tag(slug=slug, title=title)

        return await self.tags.add(tag)
