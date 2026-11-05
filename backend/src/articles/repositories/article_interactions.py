"""Просмотры и реакции посетителя."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.models.article_reaction import ArticleReaction
from src.articles.models.article_view import ArticleView


class ArticleInteractionRepository:
    """Отдельные действия посетителей."""

    def __init__(self, *, session: AsyncSession) -> None:
        """Сессия базы данных."""

        self.session = session

    async def get_view(
        self,
        *,
        article_id: int,
        visitor_id: str,
    ) -> ArticleView | None:
        """Найти просмотр посетителя."""

        return await self.session.get(ArticleView, (article_id, visitor_id))

    async def add_view(
        self,
        *,
        article_id: int,
        visitor_id: str,
    ) -> None:
        """Записать первый просмотр."""

        self.session.add(
            ArticleView(
                article_id=article_id,
                visitor_id=visitor_id,
            )
        )
        await self.session.flush()

    async def get_reaction(
        self,
        *,
        article_id: int,
        visitor_id: str,
    ) -> ArticleReaction | None:
        """Найти реакцию посетителя."""

        return await self.session.get(ArticleReaction, (article_id, visitor_id))

    async def save_reaction(self, *, reaction: ArticleReaction) -> None:
        """Сохранить реакцию."""

        self.session.add(reaction)
        await self.session.flush()

    async def delete_reaction(self, *, reaction: ArticleReaction) -> None:
        """Удалить реакцию."""

        await self.session.delete(reaction)
        await self.session.flush()
