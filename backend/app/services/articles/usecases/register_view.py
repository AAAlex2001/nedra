"""Сценарий учёта просмотра статьи."""

from app.models.article import Article
from app.services.articles.stats import ArticleStats, ArticleStatsRepository


class RegisterViewUseCase:
    """Засчитать просмотр посетителя и вернуть актуальные счётчики."""

    def __init__(self, stats: ArticleStatsRepository) -> None:
        self.stats = stats

    async def execute(self, article: Article, visitor_id: str) -> ArticleStats:
        await self.stats.add_view(article.id, visitor_id)

        return await self.stats.get_stats(article.id, visitor_id)
