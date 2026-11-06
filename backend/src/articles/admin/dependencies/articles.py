"""Зависимости публикаций."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.admin.usecases.create_article import CreateArticleUseCase
from src.articles.admin.usecases.delete_article import DeleteArticleUseCase
from src.articles.admin.usecases.get_article import GetAdminArticleUseCase
from src.articles.admin.usecases.list_articles import ListAdminArticlesUseCase
from src.articles.admin.usecases.update_article import UpdateArticleUseCase
from src.articles.repositories.article_contents import ArticleContentRepository
from src.articles.repositories.articles import ArticleRepository
from src.articles.repositories.tags import TagRepository
from src.core.database import get_session


def get_list_articles_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> ListAdminArticlesUseCase:
    """Список публикаций."""

    return ListAdminArticlesUseCase(
        articles=ArticleRepository(session=session),
        tags=TagRepository(session=session),
    )


def get_article_usecase(*, session: AsyncSession = Depends(get_session)) -> GetAdminArticleUseCase:
    """Просмотр публикации."""

    return GetAdminArticleUseCase(
        articles=ArticleRepository(session=session),
        contents=ArticleContentRepository(session=session),
        tags=TagRepository(session=session),
    )


def get_create_article_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> CreateArticleUseCase:
    """Создание публикации."""

    return CreateArticleUseCase(
        session=session,
        articles=ArticleRepository(session=session),
        contents=ArticleContentRepository(session=session),
        tags=TagRepository(session=session),
    )


def get_update_article_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> UpdateArticleUseCase:
    """Редактирование публикации."""

    return UpdateArticleUseCase(
        session=session,
        articles=ArticleRepository(session=session),
        contents=ArticleContentRepository(session=session),
        tags=TagRepository(session=session),
    )


def get_delete_article_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> DeleteArticleUseCase:
    """Удаление публикации."""

    return DeleteArticleUseCase(
        session=session,
        articles=ArticleRepository(session=session),
    )
