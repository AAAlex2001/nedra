"""Новости и блог."""

from fastapi import APIRouter, Depends, Query

from src.articles.enums import ArticleSection, ArticleSort
from src.articles.site.dependencies.articles import (
    get_article_usecase,
    get_list_articles_usecase,
    get_related_articles_usecase,
)
from src.articles.site.schemas.get_article import GetArticleRequest, GetArticleResponse
from src.articles.site.schemas.list_articles import (
    ListArticlesRequest,
    ListArticlesResponse,
)
from src.articles.site.schemas.related_articles import (
    RelatedArticleResponse,
    RelatedArticlesRequest,
)
from src.articles.site.usecases.get_article import GetArticleUseCase
from src.articles.site.usecases.list_articles import ListArticlesUseCase
from src.articles.site.usecases.list_related_articles import ListRelatedArticlesUseCase

router = APIRouter(tags=["articles"])


@router.get("/articles")
async def list_articles(
    *,
    section: ArticleSection | None = None,
    tag: str | None = None,
    search: str | None = Query(None, alias="q", max_length=100),
    sort: ArticleSort = ArticleSort.NEWEST,
    limit: int = Query(
        12,
        ge=1,
        le=50,
    ),
    offset: int = Query(0, ge=0),
    usecase: ListArticlesUseCase = Depends(get_list_articles_usecase),
) -> ListArticlesResponse:
    """Получить страницу публикаций."""

    payload = ListArticlesRequest(
        section=section,
        tag=tag,
        search=search,
        sort=sort,
        limit=limit,
        offset=offset,
    )

    return await usecase.execute(payload=payload)


@router.get("/articles/{slug}")
async def get_article(
    *,
    slug: str,
    usecase: GetArticleUseCase = Depends(get_article_usecase),
) -> GetArticleResponse:
    """Открыть публикацию."""

    payload = GetArticleRequest(slug=slug)

    return await usecase.execute(payload=payload)


@router.get("/articles/{slug}/related")
async def list_related(
    *,
    slug: str,
    limit: int = Query(
        10,
        ge=1,
        le=20,
    ),
    usecase: ListRelatedArticlesUseCase = Depends(get_related_articles_usecase),
) -> list[RelatedArticleResponse]:
    """Подобрать другие публикации."""

    payload = RelatedArticlesRequest(
        slug=slug,
        limit=limit,
    )

    return await usecase.execute(payload=payload)
