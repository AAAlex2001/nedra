from fastapi import APIRouter, Depends, Query

from app.dependencies.articles import (
    get_article_repository,
    get_published_article,
    get_register_view_usecase,
    get_remove_reaction_usecase,
    get_set_reaction_usecase,
    get_tag_repository,
)
from app.dependencies.visitor import get_visitor_id
from app.models.article import Article
from app.schemas.article import (
    ArticleCardSchema,
    ArticleListSchema,
    ArticleSchema,
    ArticleStatsSchema,
    ReactionInSchema,
    Section,
    TagSchema,
)
from app.services.articles.repo import ArticleRepository
from app.services.articles.tags import TagRepository
from app.services.articles.usecases.register_view import RegisterViewUseCase
from app.services.articles.usecases.remove_reaction import RemoveReactionUseCase
from app.services.articles.usecases.set_reaction import SetReactionUseCase


router = APIRouter(tags=["articles"])


@router.get("/articles")
async def get_articles(
    section: Section | None = Query(None, description="Раздел: blog или news"),
    tag: str | None = Query(None, description="Slug тега для фильтрации"),
    limit: int = Query(12, ge=1, le=50),
    offset: int = Query(0, ge=0),
    articles: ArticleRepository = Depends(get_article_repository),
) -> ArticleListSchema:
    """Список опубликованных статей."""

    items, total = await articles.list_published(section, tag, limit, offset)

    return ArticleListSchema(
        articles=[ArticleCardSchema.model_validate(item) for item in items],
        total=total,
    )


@router.get("/tags")
async def get_tags(
    section: Section | None = Query(None, description="Раздел: только теги его опубликованных статей"),
    tags: TagRepository = Depends(get_tag_repository),
) -> list[TagSchema]:
    """Теги для фильтра списка статей."""

    items = await tags.list_all(section)

    return [TagSchema.model_validate(item) for item in items]


@router.get("/articles/{slug}")
async def get_article(
    article: Article = Depends(get_published_article),
) -> ArticleSchema:
    """Статья целиком."""

    return ArticleSchema.model_validate(article)


@router.get("/articles/{slug}/related")
async def get_related_articles(
    limit: int = Query(10, ge=1, le=20),
    article: Article = Depends(get_published_article),
    articles: ArticleRepository = Depends(get_article_repository),
) -> list[ArticleCardSchema]:
    """Блок «Смотрите также»."""

    related = await articles.get_related(article, limit)

    return [ArticleCardSchema.model_validate(item) for item in related]


@router.post("/articles/{slug}/view")
async def register_view(
    article: Article = Depends(get_published_article),
    visitor_id: str = Depends(get_visitor_id),
    usecase: RegisterViewUseCase = Depends(get_register_view_usecase),
) -> ArticleStatsSchema:
    """Засчитать просмотр и вернуть актуальные счётчики."""

    stats = await usecase.execute(article, visitor_id)

    return ArticleStatsSchema.model_validate(stats)


@router.put("/articles/{slug}/reaction")
async def set_reaction(
    payload: ReactionInSchema,
    article: Article = Depends(get_published_article),
    visitor_id: str = Depends(get_visitor_id),
    usecase: SetReactionUseCase = Depends(get_set_reaction_usecase),
) -> ArticleStatsSchema:
    """Поставить лайк или дизлайк."""

    stats = await usecase.execute(article, visitor_id, payload.value)

    return ArticleStatsSchema.model_validate(stats)


@router.delete("/articles/{slug}/reaction")
async def remove_reaction(
    article: Article = Depends(get_published_article),
    visitor_id: str = Depends(get_visitor_id),
    usecase: RemoveReactionUseCase = Depends(get_remove_reaction_usecase),
) -> ArticleStatsSchema:
    """Снять свою реакцию."""

    stats = await usecase.execute(article, visitor_id)

    return ArticleStatsSchema.model_validate(stats)
