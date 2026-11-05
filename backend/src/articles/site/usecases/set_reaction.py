"""Установка реакции на публикацию."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.exceptions import ArticleNotFoundError
from src.articles.models.article_reaction import ArticleReaction
from src.articles.repositories.article_interactions import ArticleInteractionRepository
from src.articles.repositories.articles import ArticleRepository
from src.articles.site.schemas.reaction import ArticleCountersResponse, SetReactionRequest


class SetArticleReactionUseCase:
    """Добавление или замена реакции."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        articles: ArticleRepository,
        interactions: ArticleInteractionRepository,
    ) -> None:
        """Публикации и реакции."""

        self.session = session
        self.articles = articles
        self.interactions = interactions

    async def execute(
        self,
        *,
        slug: str,
        visitor_id: str,
        payload: SetReactionRequest,
    ) -> ArticleCountersResponse:
        """Записать реакцию посетителя."""

        article = await self.articles.get_published_for_update(slug=slug)

        if article is None:
            raise ArticleNotFoundError()

        reaction = await self.interactions.get_reaction(
            article_id=article.id,
            visitor_id=visitor_id,
        )

        if reaction is not None and reaction.value == payload.value:
            return ArticleCountersResponse.from_model(
                article=article,
                reaction_value=reaction.value,
            )

        if reaction is None:
            reaction = ArticleReaction(
                article_id=article.id,
                visitor_id=visitor_id,
            )
        elif reaction.value == 1:
            article.likes_count -= 1
        else:
            article.dislikes_count -= 1

        reaction.value = payload.value

        if payload.value == 1:
            article.likes_count += 1
        else:
            article.dislikes_count += 1

        await self.interactions.save_reaction(reaction=reaction)
        await self.articles.save(article=article)
        response = ArticleCountersResponse.from_model(
            article=article,
            reaction_value=reaction.value,
        )
        await self.session.commit()

        return response
