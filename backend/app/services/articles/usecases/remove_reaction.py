"""Сценарий снятия реакции."""

from app.models.article import Article
from app.services.articles.stats import ArticleStats, ArticleStatsRepository


class RemoveReactionUseCase:
    """Снять реакцию посетителя, если она была, и вернуть актуальные счётчики."""

    def __init__(self, stats: ArticleStatsRepository) -> None:
        self.stats = stats

    async def execute(self, article: Article, visitor_id: str) -> ArticleStats:
        reaction = await self.stats.get_reaction(article.id, visitor_id)

        if reaction is not None:
            await self.stats.delete_reaction(reaction)

        return await self.stats.get_stats(article.id, visitor_id)
