"""Зависимости публикаций."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.repositories.tags import TagRepository
from src.articles.site.usecases.list_tags import ListTagsUseCase
from src.core.database import get_session


def get_list_tags_usecase(*, session: AsyncSession = Depends(get_session)) -> ListTagsUseCase:
    """Направления публикаций."""

    return ListTagsUseCase(tags=TagRepository(session=session))
