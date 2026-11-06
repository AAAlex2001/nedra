"""Просмотры и реакции."""

from fastapi import APIRouter, Depends

from src.articles.site.dependencies.interactions import (
    get_register_view_usecase,
    get_remove_reaction_usecase,
    get_set_reaction_usecase,
)
from src.articles.site.schemas.reaction import (
    ArticleCountersResponse,
    SetReactionRequest,
)
from src.articles.site.usecases.register_view import RegisterArticleViewUseCase
from src.articles.site.usecases.remove_reaction import RemoveArticleReactionUseCase
from src.articles.site.usecases.set_reaction import SetArticleReactionUseCase
from src.articles.site.visitor import get_visitor_id

router = APIRouter(tags=["articles"])


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
