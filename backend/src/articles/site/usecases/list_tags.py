"""Направления публикаций."""

from src.articles.repositories.tags import TagRepository
from src.articles.site.schemas.list_tags import ListedTagResponse, ListTagsRequest


class ListTagsUseCase:
    """Теги для фильтра на сайте."""

    def __init__(self, *, tags: TagRepository) -> None:
        """Теги публикаций."""

        self.tags = tags

    async def execute(self, *, payload: ListTagsRequest) -> list[ListedTagResponse]:
        """Получить направления."""

        tags = await self.tags.list_all(section=payload.section)
        return [ListedTagResponse.from_model(tag=tag) for tag in tags]
