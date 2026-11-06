"""Направления публикаций."""

from fastapi import APIRouter, Depends

from src.articles.admin.dependencies.tags import (
    get_create_tag_usecase,
    get_delete_tag_usecase,
    get_list_tags_usecase,
)
from src.articles.admin.schemas.tag import AdminTagResponse, CreateTagRequest
from src.articles.admin.usecases.create_tag import CreateTagUseCase
from src.articles.admin.usecases.delete_tag import DeleteTagUseCase
from src.articles.admin.usecases.list_tags import ListAdminTagsUseCase
from src.auth.admin.access import require_admin

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)


@router.get("/tags")
async def list_tags(
    *,
    usecase: ListAdminTagsUseCase = Depends(get_list_tags_usecase),
) -> list[AdminTagResponse]:
    """Получить теги редактора."""

    return await usecase.execute()


@router.post("/tags", status_code=201)
async def create_tag(
    *,
    payload: CreateTagRequest,
    usecase: CreateTagUseCase = Depends(get_create_tag_usecase),
) -> AdminTagResponse:
    """Создать тег."""

    return await usecase.execute(payload=payload)


@router.delete("/tags/{tag_id}", status_code=204)
async def delete_tag(
    *,
    tag_id: int,
    usecase: DeleteTagUseCase = Depends(get_delete_tag_usecase),
) -> None:
    """Удалить тег."""

    await usecase.execute(tag_id=tag_id)
