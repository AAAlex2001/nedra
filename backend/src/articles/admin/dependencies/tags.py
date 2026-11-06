"""Зависимости публикаций."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.admin.usecases.create_tag import CreateTagUseCase
from src.articles.admin.usecases.delete_tag import DeleteTagUseCase
from src.articles.admin.usecases.list_tags import ListAdminTagsUseCase
from src.articles.repositories.tags import TagRepository
from src.core.database import get_session


def get_list_tags_usecase(*, session: AsyncSession = Depends(get_session)) -> ListAdminTagsUseCase:
    """Все теги."""

    return ListAdminTagsUseCase(
        tags=TagRepository(session=session),
    )


def get_create_tag_usecase(*, session: AsyncSession = Depends(get_session)) -> CreateTagUseCase:
    """Создание тега."""

    return CreateTagUseCase(
        session=session,
        tags=TagRepository(session=session),
    )


def get_delete_tag_usecase(*, session: AsyncSession = Depends(get_session)) -> DeleteTagUseCase:
    """Удаление тега."""

    return DeleteTagUseCase(
        session=session,
        tags=TagRepository(session=session),
    )
