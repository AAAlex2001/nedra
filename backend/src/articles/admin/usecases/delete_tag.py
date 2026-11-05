"""Удаление направления публикаций."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.exceptions import TagNotFoundError
from src.articles.repositories.tags import TagRepository


class DeleteTagUseCase:
    """Удаление тега."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        tags: TagRepository,
    ) -> None:
        """Сессия и теги."""

        self.session = session
        self.tags = tags

    async def execute(self, *, tag_id: int) -> None:
        """Удалить тег и его привязки."""

        tag = await self.tags.get_by_id(tag_id=tag_id)

        if tag is None:
            raise TagNotFoundError()

        await self.tags.delete(tag=tag)
        await self.session.commit()
