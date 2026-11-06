"""Зависимости публикаций."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.repositories.article_interactions import ArticleInteractionRepository
from src.articles.repositories.articles import ArticleRepository
from src.articles.site.usecases.register_view import RegisterArticleViewUseCase
from src.articles.site.usecases.remove_reaction import RemoveArticleReactionUseCase
from src.articles.site.usecases.set_reaction import SetArticleReactionUseCase
from src.core.database import get_session


def get_register_view_usecase(
    *,
    session: AsyncSession = Depends(get_session),
) -> RegisterArticleViewUseCase:
    """Учёт просмотров."""

    return RegisterArticleViewUseCase(
        session=session,
        articles=ArticleRepository(session=session),
        interactions=ArticleInteractionRepository(session=session),
    )


def get_set_reaction_usecase(
    *,
    session: AsyncSession = Depends(get_session),
) -> SetArticleReactionUseCase:
    """Установка реакции."""

    return SetArticleReactionUseCase(
        session=session,
        articles=ArticleRepository(session=session),
        interactions=ArticleInteractionRepository(session=session),
    )


def get_remove_reaction_usecase(
    *,
    session: AsyncSession = Depends(get_session),
) -> RemoveArticleReactionUseCase:
    """Удаление реакции."""

    return RemoveArticleReactionUseCase(
        session=session,
        articles=ArticleRepository(session=session),
        interactions=ArticleInteractionRepository(session=session),
    )
