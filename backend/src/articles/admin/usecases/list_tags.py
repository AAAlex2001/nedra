"""Теги редактора."""

from src.articles.admin.schemas.tag import AdminTagResponse
from src.articles.repositories.tags import TagRepository


class ListAdminTagsUseCase:
    """Все направления публикаций."""

    def __init__(self, *, tags: TagRepository) -> None:
        """Хранилище тегов."""

        self.tags = tags

    async def execute(self) -> list[AdminTagResponse]:
        """Получить теги редактора."""

        tags = await self.tags.list_all()

        return [AdminTagResponse.from_model(tag=tag) for tag in tags]
