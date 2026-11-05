"""Новости и блог."""

from fastapi import APIRouter, Depends, Query

from src.articles.enums import ArticleSection, ArticleSort
from src.articles.schemas.article import (
    ArticleCardResponse,
    ArticleListResponse,
    ArticleResponse,
    TagResponse,
)
from src.articles.site.dependencies import (
    get_article_usecase,
    get_list_articles_usecase,
    get_list_tags_usecase,
    get_register_view_usecase,
    get_related_articles_usecase,
    get_remove_reaction_usecase,
    get_set_reaction_usecase,
)
from src.articles.site.schemas.reaction import ArticleCountersResponse, SetReactionRequest
from src.articles.site.usecases.get_article import GetArticleUseCase
from src.articles.site.usecases.list_articles import ListArticlesUseCase
from src.articles.site.usecases.list_related_articles import ListRelatedArticlesUseCase
from src.articles.site.usecases.list_tags import ListTagsUseCase
from src.articles.site.usecases.register_view import RegisterArticleViewUseCase
from src.articles.site.usecases.remove_reaction import RemoveArticleReactionUseCase
from src.articles.site.usecases.set_reaction import SetArticleReactionUseCase
from src.articles.site.visitor import get_visitor_id

router = APIRouter(tags=["articles"])


@router.get("/articles")
async def list_articles(
    *,
    section: ArticleSection | None = None,
    tag: str | None = None,
    q: str | None = Query(None, max_length=100),
    sort: ArticleSort = ArticleSort.NEWEST,
    limit: int = Query(
        12,
        ge=1,
        le=50,
    ),
    offset: int = Query(0, ge=0),
    usecase: ListArticlesUseCase = Depends(get_list_articles_usecase),
) -> ArticleListResponse:
    """Получить страницу публикаций."""

    return await usecase.execute(
        section=section,
        tag_slug=tag,
        search=q,
        sort=sort,
        limit=limit,
        offset=offset,
    )


@router.get("/tags")
async def list_tags(
    *,
    section: ArticleSection | None = None,
    usecase: ListTagsUseCase = Depends(get_list_tags_usecase),
) -> list[TagResponse]:
    """Получить направления."""

    return await usecase.execute(section=section)


@router.get("/articles/{slug}")
async def get_article(
    *,
    slug: str,
    usecase: GetArticleUseCase = Depends(get_article_usecase),
) -> ArticleResponse:
    """Открыть публикацию."""

    return await usecase.execute(slug=slug)


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
) -> list[ArticleCardResponse]:
    """Подобрать другие публикации."""

    return await usecase.execute(
        slug=slug,
        limit=limit,
    )


@router.post("/articles/{slug}/view")
async def register_view(
    *,
    slug: str,
    visitor_id: str = Depends(get_visitor_id),
    usecase: RegisterArticleViewUseCase = Depends(get_register_view_usecase),
) -> ArticleCountersResponse:
    """Засчитать просмотр."""

    return await usecase.execute(
        slug=slug,
        visitor_id=visitor_id,
    )


@router.put("/articles/{slug}/reaction")
async def set_reaction(
    *,
    slug: str,
    payload: SetReactionRequest,
    visitor_id: str = Depends(get_visitor_id),
    usecase: SetArticleReactionUseCase = Depends(get_set_reaction_usecase),
) -> ArticleCountersResponse:
    """Поставить реакцию."""

    return await usecase.execute(
        slug=slug,
        visitor_id=visitor_id,
        payload=payload,
    )


@router.delete("/articles/{slug}/reaction")
async def remove_reaction(
    *,
    slug: str,
    visitor_id: str = Depends(get_visitor_id),
    usecase: RemoveArticleReactionUseCase = Depends(get_remove_reaction_usecase),
) -> ArticleCountersResponse:
    """Снять реакцию."""

    return await usecase.execute(
        slug=slug,
        visitor_id=visitor_id,
    )
