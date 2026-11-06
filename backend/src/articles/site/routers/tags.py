"""Направления публикаций."""

from fastapi import APIRouter, Depends

from src.articles.enums import ArticleSection
from src.articles.site.dependencies.tags import get_list_tags_usecase
from src.articles.site.schemas.list_tags import ListedTagResponse, ListTagsRequest
from src.articles.site.usecases.list_tags import ListTagsUseCase

router = APIRouter(tags=["articles"])


@router.get("/tags")
async def list_tags(
    *,
    section: ArticleSection | None = None,
    usecase: ListTagsUseCase = Depends(get_list_tags_usecase),
) -> list[ListedTagResponse]:
    """Получить направления."""

    payload = ListTagsRequest(section=section)

    return await usecase.execute(payload=payload)
