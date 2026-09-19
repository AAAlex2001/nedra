"""Просмотры и реакции: счётчики статьи и записи о посетителях."""

from dataclasses import dataclass

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article, ArticleReaction, ArticleView

LIKE = 1
DISLIKE = -1


@dataclass(frozen=True)
class ArticleStats:
    """Счётчики статьи и реакция текущего посетителя."""

    views_count: int
    likes_count: int
    dislikes_count: int
    my_reaction: int | None


class ArticleStatsRepository:
    """Запросы к article_views, article_reactions и счётчикам в articles.

    Арифметика счётчиков выполняется в базе, а не в Python, чтобы параллельные
    запросы не затирали обновления друг друга.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_stats(self, article_id: int, visitor_id: str) -> ArticleStats:
        """Актуальные счётчики статьи и реакция этого посетителя.

        Читает колонки напрямую из базы, а не из объекта в сессии:
        после массового UPDATE значения в объекте могут быть устаревшими.
        """

        stmt = select(
            Article.views_count, Article.likes_count, Article.dislikes_count
        ).where(Article.id == article_id)
        result = await self.db.execute(stmt)
        counters = result.one()

        reaction = await self.get_reaction(article_id, visitor_id)
        my_reaction = None
        if reaction is not None:
            my_reaction = reaction.value

        return ArticleStats(
            views_count=counters.views_count,
            likes_count=counters.likes_count,
            dislikes_count=counters.dislikes_count,
            my_reaction=my_reaction,
        )

    async def add_view(self, article_id: int, visitor_id: str) -> bool:
        """Засчитать просмотр. Возвращает False, если этот посетитель уже учтён.

        Один посетитель учитывается один раз: это гарантирует составной
        первичный ключ (article_id, visitor_id). Если два запроса пришли
        одновременно и оба прошли проверку, второй упадёт на IntegrityError —
        тогда просмотр уже учтён и делать ничего не нужно.
        """

        already_viewed = await self.db.get(ArticleView, (article_id, visitor_id))
        if already_viewed is not None:
            return False

        self.db.add(ArticleView(article_id=article_id, visitor_id=visitor_id))

        try:
            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            return False

        await self.db.execute(
            update(Article)
            .where(Article.id == article_id)
            .values(views_count=Article.views_count + 1)
        )
        await self.db.commit()

        return True

    async def get_reaction(self, article_id: int, visitor_id: str) -> ArticleReaction | None:
        """Реакция посетителя на статью или None."""

        return await self.db.get(ArticleReaction, (article_id, visitor_id))

    async def add_reaction(self, article_id: int, visitor_id: str, value: int) -> bool:
        """Первая реакция посетителя: запись в таблицу плюс единица в нужный счётчик."""

        self.db.add(
            ArticleReaction(article_id=article_id, visitor_id=visitor_id, value=value)
        )

        try:
            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            return False

        if value == LIKE:
            await self.update_counters(article_id, likes=1)
        else:
            await self.update_counters(article_id, dislikes=1)

        await self.db.commit()

        return True

    async def change_reaction(self, reaction: ArticleReaction, value: int) -> None:
        """Смена лайка на дизлайк или наоборот: единица переносится между счётчиками."""

        reaction.value = value

        if value == LIKE:
            await self.update_counters(reaction.article_id, likes=1, dislikes=-1)
        else:
            await self.update_counters(reaction.article_id, likes=-1, dislikes=1)

        await self.db.commit()

    async def delete_reaction(self, reaction: ArticleReaction) -> None:
        """Снять реакцию и уменьшить соответствующий счётчик."""

        if reaction.value == LIKE:
            await self.update_counters(reaction.article_id, likes=-1)
        else:
            await self.update_counters(reaction.article_id, dislikes=-1)

        await self.db.delete(reaction)
        await self.db.commit()

    async def update_counters(self, article_id: int, likes: int = 0, dislikes: int = 0) -> None:
        """Изменить счётчики лайков и дизлайков на указанные величины."""

        await self.db.execute(
            update(Article)
            .where(Article.id == article_id)
            .values(
                likes_count=Article.likes_count + likes,
                dislikes_count=Article.dislikes_count + dislikes,
            )
        )
