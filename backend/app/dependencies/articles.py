"""Статьи: репозитории, загрузка статьи по slug или id, фабрики сценариев."""

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.article import Article
from app.services.articles.repo import ArticleRepository
from app.services.articles.stats import ArticleStatsRepository
from app.services.articles.tags import TagRepository
from app.services.articles.usecases.create_article import CreateArticleUseCase
from app.services.articles.usecases.create_tag import CreateTagUseCase
from app.services.articles.usecases.register_view import RegisterViewUseCase
from app.services.articles.usecases.remove_reaction import RemoveReactionUseCase
from app.services.articles.usecases.set_reaction import SetReactionUseCase
from app.services.articles.usecases.update_article import UpdateArticleUseCase


def get_article_repository(
    session: AsyncSession = Depends(get_session),
) -> ArticleRepository:
    """Репозиторий статей с сессией текущего запроса."""

    return ArticleRepository(session)


def get_tag_repository(
    session: AsyncSession = Depends(get_session),
) -> TagRepository:
    """Репозиторий тегов с сессией текущего запроса."""

    return TagRepository(session)


def get_stats_repository(
    session: AsyncSession = Depends(get_session),
) -> ArticleStatsRepository:
    """Репозиторий просмотров и реакций с сессией текущего запроса."""

    return ArticleStatsRepository(session)


async def get_published_article(
    slug: str,
    articles: ArticleRepository = Depends(get_article_repository),
) -> Article:
    """Опубликованная статья из пути /articles/{slug}. Черновик или чужой slug — 404."""

    article = await articles.get_published(slug)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Статья «{slug}» не найдена",
        )

    return article


async def get_article_by_id(
    article_id: int,
    articles: ArticleRepository = Depends(get_article_repository),
) -> Article:
    """Статья из пути /admin/articles/{article_id}, черновики тоже. Нет — 404."""

    article = await articles.get_by_id(article_id)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Статья с ID {article_id} не найдена",
        )

    return article


def get_create_article_usecase(
    articles: ArticleRepository = Depends(get_article_repository),
    tags: TagRepository = Depends(get_tag_repository),
) -> CreateArticleUseCase:
    """Сценарий создания статьи."""

    return CreateArticleUseCase(articles, tags)


def get_update_article_usecase(
    articles: ArticleRepository = Depends(get_article_repository),
    tags: TagRepository = Depends(get_tag_repository),
) -> UpdateArticleUseCase:
    """Сценарий обновления статьи."""

    return UpdateArticleUseCase(articles, tags)


def get_create_tag_usecase(
    tags: TagRepository = Depends(get_tag_repository),
) -> CreateTagUseCase:
    """Сценарий создания тега."""

    return CreateTagUseCase(tags)


def get_register_view_usecase(
    stats: ArticleStatsRepository = Depends(get_stats_repository),
) -> RegisterViewUseCase:
    """Сценарий учёта просмотра."""

    return RegisterViewUseCase(stats)


def get_set_reaction_usecase(
    stats: ArticleStatsRepository = Depends(get_stats_repository),
) -> SetReactionUseCase:
    """Сценарий лайка или дизлайка."""

    return SetReactionUseCase(stats)


def get_remove_reaction_usecase(
    stats: ArticleStatsRepository = Depends(get_stats_repository),
) -> RemoveReactionUseCase:
    """Сценарий снятия реакции."""

    return RemoveReactionUseCase(stats)
