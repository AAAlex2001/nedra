"""Зависимости публикаций."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.repositories.article_contents import ArticleContentRepository
from src.articles.repositories.articles import ArticleRepository
from src.articles.repositories.tags import TagRepository
from src.articles.site.usecases.get_article import GetArticleUseCase
from src.articles.site.usecases.list_articles import ListArticlesUseCase
from src.articles.site.usecases.list_related_articles import ListRelatedArticlesUseCase
from src.core.database import get_session


def get_article_usecase(*, session: AsyncSession = Depends(get_session)) -> GetArticleUseCase:
    """Просмотр публикации."""

    return GetArticleUseCase(
        articles=ArticleRepository(session=session),
        contents=ArticleContentRepository(session=session),
        tags=TagRepository(session=session),
    )


def get_list_articles_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> ListArticlesUseCase:
    """Список публикаций."""

    return ListArticlesUseCase(
        articles=ArticleRepository(session=session),
        tags=TagRepository(session=session),
    )


def get_related_articles_usecase(
    *,
    session: AsyncSession = Depends(get_session),
) -> ListRelatedArticlesUseCase:
    """Похожие публикации."""

    return ListRelatedArticlesUseCase(
        articles=ArticleRepository(session=session),
        tags=TagRepository(session=session),
    )
