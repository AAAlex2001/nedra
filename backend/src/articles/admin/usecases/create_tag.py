"""Создание направления публикаций."""

from slugify import slugify
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from src.articles.admin.schemas.tag import AdminTagResponse, CreateTagRequest
from src.articles.exceptions import ArticleConflictError
from src.articles.models.tag import Tag
from src.articles.options import TAG_SLUG_MAX_LENGTH
from src.articles.repositories.tags import TagRepository


class CreateTagUseCase:
    """Новый тег редактора."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        tags: TagRepository,
    ) -> None:
        """Сессия и теги."""

        self.session = session
        self.tags = tags

    async def execute(self, *, payload: CreateTagRequest) -> AdminTagResponse:
        """Создать тег со свободным адресом."""

        base_slug = slugify(payload.title, max_length=TAG_SLUG_MAX_LENGTH) or "tag"
        slug = base_slug
        suffix = 2

        while await self.tags.get_by_slug(slug=slug) is not None:
            slug = f"{base_slug}-{suffix}"
            suffix += 1

        tag = Tag(
            title=payload.title,
            slug=slug,
        )

        try:
            await self.tags.save(tag=tag)
            response = AdminTagResponse.from_model(tag=tag)
            await self.session.commit()
        except IntegrityError as error:
            await self.session.rollback()
            raise ArticleConflictError() from error

        return response
