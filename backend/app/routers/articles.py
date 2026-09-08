from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies import get_article_service, get_visitor_id
from app.schemas.articles import (
    ArticleCardSchema,
    ArticleListSchema,
    ArticleSchema,
    ArticleStatsSchema,
    ReactionInSchema,
    TagSchema,
)
from app.services.articles import ArticleService
from app.services.exceptions import ArticleNotFoundError


router = APIRouter(tags=["articles"])


@router.get("/articles")
async def get_articles(
    tag: str | None = Query(None, description="Slug тега для фильтрации"),
    limit: int = Query(12, ge=1, le=50),
    offset: int = Query(0, ge=0),
    service: ArticleService = Depends(get_article_service),
) -> ArticleListSchema:
    """Список опубликованных статей."""

    articles, total = await service.list_published(tag, limit, offset)

    return ArticleListSchema(
        articles=[ArticleCardSchema.model_validate(article) for article in articles],
        total=total,
    )


@router.get("/tags")
async def get_tags(
    service: ArticleService = Depends(get_article_service),
) -> list[TagSchema]:
    """Все теги для фильтра."""

    return [TagSchema.model_validate(tag) for tag in await service.list_tags()]


@router.get("/articles/{slug}")
async def get_article(
    slug: str,
    service: ArticleService = Depends(get_article_service),
) -> ArticleSchema:
    """Статья целиком."""

    try:
        article = await service.get_published(slug)
    except ArticleNotFoundError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(error)) from error

    return ArticleSchema.model_validate(article)


@router.get("/articles/{slug}/related")
async def get_related_articles(
    slug: str,
    limit: int = Query(10, ge=1, le=20),
    service: ArticleService = Depends(get_article_service),
) -> list[ArticleCardSchema]:
    """Блок «Смотрите также»."""

    try:
        article = await service.get_published(slug)
    except ArticleNotFoundError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(error)) from error

    related = await service.get_related(article, limit)

    return [ArticleCardSchema.model_validate(item) for item in related]


@router.post("/articles/{slug}/view")
async def register_view(
    slug: str,
    visitor_id: str = Depends(get_visitor_id),
    service: ArticleService = Depends(get_article_service),
) -> ArticleStatsSchema:
    """Засчитать просмотр и вернуть актуальные счётчики."""

    try:
        article = await service.get_published(slug)
    except ArticleNotFoundError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(error)) from error

    await service.register_view(article, visitor_id)
    stats = await service.get_stats(article.id, visitor_id)

    return ArticleStatsSchema.model_validate(stats)


@router.put("/articles/{slug}/reaction")
async def set_reaction(
    slug: str,
    payload: ReactionInSchema,
    visitor_id: str = Depends(get_visitor_id),
    service: ArticleService = Depends(get_article_service),
) -> ArticleStatsSchema:
    """Поставить лайк или дизлайк."""

    try:
        article = await service.get_published(slug)
    except ArticleNotFoundError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(error)) from error

    await service.set_reaction(article, visitor_id, payload.value)
    stats = await service.get_stats(article.id, visitor_id)

    return ArticleStatsSchema.model_validate(stats)


@router.delete("/articles/{slug}/reaction")
async def remove_reaction(
    slug: str,
    visitor_id: str = Depends(get_visitor_id),
    service: ArticleService = Depends(get_article_service),
) -> ArticleStatsSchema:
    """Снять свою реакцию."""

    try:
        article = await service.get_published(slug)
    except ArticleNotFoundError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(error)) from error

    await service.remove_reaction(article, visitor_id)
    stats = await service.get_stats(article.id, visitor_id)

    return ArticleStatsSchema.model_validate(stats)
