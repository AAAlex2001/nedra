"""Редактор новостей и блога."""

from fastapi import APIRouter, Depends, Query

from src.articles.admin.dependencies.articles import (
    get_article_usecase,
    get_create_article_usecase,
    get_delete_article_usecase,
    get_list_articles_usecase,
    get_update_article_usecase,
)
from src.articles.admin.schemas.create_article import (
    CreateArticleRequest,
    CreateArticleResponse,
)
from src.articles.admin.schemas.get_article import GetArticleRequest, GetArticleResponse
from src.articles.admin.schemas.list_articles import (
    ListArticlesRequest,
    ListArticlesResponse,
)
from src.articles.admin.schemas.update_article import (
    UpdateArticleRequest,
    UpdateArticleResponse,
)
from src.articles.admin.usecases.create_article import CreateArticleUseCase
from src.articles.admin.usecases.delete_article import DeleteArticleUseCase
from src.articles.admin.usecases.get_article import GetAdminArticleUseCase
from src.articles.admin.usecases.list_articles import ListAdminArticlesUseCase
from src.articles.admin.usecases.update_article import UpdateArticleUseCase
from src.articles.enums import AdminArticleSort, ArticleSection
from src.auth.admin.access import require_admin

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)


@router.get("/articles")
async def list_articles(
    *,
    section: ArticleSection | None = None,
    sort: AdminArticleSort = AdminArticleSort.NEW,
    search: str | None = Query(None, alias="q", max_length=100),
    limit: int = Query(
        20,
        ge=1,
        le=100,
    ),
    offset: int = Query(0, ge=0),
    usecase: ListAdminArticlesUseCase = Depends(get_list_articles_usecase),
) -> ListArticlesResponse:
    """Получить страницу публикаций."""

    payload = ListArticlesRequest(
        section=section,
        search=search,
        sort=sort,
        limit=limit,
        offset=offset,
    )

    return await usecase.execute(payload=payload)


@router.get("/articles/{article_id}")
async def get_article(
    *,
    article_id: int,
    usecase: GetAdminArticleUseCase = Depends(get_article_usecase),
) -> GetArticleResponse:
    """Открыть статью редактора."""

    payload = GetArticleRequest(article_id=article_id)

    return await usecase.execute(payload=payload)


@router.post("/articles", status_code=201)
async def create_article(
    *,
    payload: CreateArticleRequest,
    usecase: CreateArticleUseCase = Depends(get_create_article_usecase),
) -> CreateArticleResponse:
    """Создать публикацию."""

    return await usecase.execute(payload=payload)


@router.patch("/articles/{article_id}")
async def update_article(
    *,
    article_id: int,
    payload: UpdateArticleRequest,
    usecase: UpdateArticleUseCase = Depends(get_update_article_usecase),
) -> UpdateArticleResponse:
    """Сохранить изменения публикации."""

    return await usecase.execute(
        article_id=article_id,
        payload=payload,
    )


@router.delete("/articles/{article_id}", status_code=204)
async def delete_article(
    *,
    article_id: int,
    usecase: DeleteArticleUseCase = Depends(get_delete_article_usecase),
) -> None:
    """Удалить публикацию."""

    await usecase.execute(article_id=article_id)
