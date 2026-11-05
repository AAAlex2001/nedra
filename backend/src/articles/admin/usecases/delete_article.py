"""Удаление публикации."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.exceptions import ArticleNotFoundError
from src.articles.repositories.articles import ArticleRepository


class DeleteArticleUseCase:
    """Удаление статьи и её связей."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        articles: ArticleRepository,
    ) -> None:
        """Сессия и публикации."""

        self.session = session
        self.articles = articles

    async def execute(self, *, article_id: int) -> None:
        """Удалить публикацию."""

        article = await self.articles.get_for_update(article_id=article_id)

        if article is None:
            raise ArticleNotFoundError()

        await self.articles.delete(article=article)
        await self.session.commit()
