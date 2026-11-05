"""Учёт просмотра публикации."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.exceptions import ArticleNotFoundError
from src.articles.repositories.article_interactions import ArticleInteractionRepository
from src.articles.repositories.articles import ArticleRepository
from src.articles.site.schemas.reaction import ArticleCountersResponse


class RegisterArticleViewUseCase:
    """Первый просмотр посетителя."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        articles: ArticleRepository,
        interactions: ArticleInteractionRepository,
    ) -> None:
        """Публикации и действия посетителей."""

        self.session = session
        self.articles = articles
        self.interactions = interactions

    async def execute(
        self,
        *,
        slug: str,
        visitor_id: str,
    ) -> ArticleCountersResponse:
        """Засчитать уникальный просмотр."""

        article = await self.articles.get_published_for_update(slug=slug)

        if article is None:
            raise ArticleNotFoundError()

        view = await self.interactions.get_view(
            article_id=article.id,
            visitor_id=visitor_id,
        )

        if view is None:
            await self.interactions.add_view(
                article_id=article.id,
                visitor_id=visitor_id,
            )
            article.views_count += 1
            await self.articles.save(article=article)

        reaction = await self.interactions.get_reaction(
            article_id=article.id,
            visitor_id=visitor_id,
        )
        response = ArticleCountersResponse.from_model(
            article=article,
            reaction_value=reaction.value if reaction else None,
        )
        await self.session.commit()

        return response
