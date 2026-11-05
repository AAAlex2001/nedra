"""Направления публикаций."""

from src.articles.enums import ArticleSection
from src.articles.repositories.tags import TagRepository
from src.articles.schemas.article import TagResponse


class ListTagsUseCase:
    """Теги для фильтра на сайте."""

    def __init__(self, *, tags: TagRepository) -> None:
        """Теги публикаций."""

        self.tags = tags

    async def execute(self, *, section: ArticleSection | None) -> list[TagResponse]:
        """Получить направления."""

        tags = await self.tags.list_all(section=section)
        return [TagResponse.from_model(tag=tag) for tag in tags]
