"""Сценарий лайка или дизлайка."""

from app.models.article import Article
from app.services.articles.stats import ArticleStats, ArticleStatsRepository


class SetReactionUseCase:
    """Поставить лайк (1) или дизлайк (-1) и вернуть актуальные счётчики.

    Повторный клик тем же значением ничего не меняет.
    Другое значение переключает реакцию и переносит единицу между счётчиками.
    """

    def __init__(self, stats: ArticleStatsRepository) -> None:
        self.stats = stats

    async def execute(self, article: Article, visitor_id: str, value: int) -> ArticleStats:
        reaction = await self.stats.get_reaction(article.id, visitor_id)

        if reaction is None:
            await self.stats.add_reaction(article.id, visitor_id, value)
        elif reaction.value != value:
            await self.stats.change_reaction(reaction, value)

        return await self.stats.get_stats(article.id, visitor_id)
