"""Репозиторий тегов: только запросы к таблице tags."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article, Tag, article_tags
from app.services.articles.exceptions import TagNotFoundError
from app.services.articles.repo import PUBLISHED


class TagRepository:
    """Доступ к таблице tags. Сессию получает снаружи, коммитит сам."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list(self, section: str | None) -> list[Tag]:
        """Теги по алфавиту.

        Если передан section — только теги, которыми отмечена хотя бы одна
        опубликованная статья этого раздела. Без section — все теги, для админки.
        """

        stmt = select(Tag).order_by(Tag.title)

        if section:
            stmt = (
                select(Tag)
                .join(article_tags, article_tags.c.tag_id == Tag.id)
                .join(Article, Article.id == article_tags.c.article_id)
                .where(PUBLISHED, Article.section == section)
                .distinct()
                .order_by(Tag.title)
            )

        result = await self.db.execute(stmt)

        return list(result.scalars().all())

    async def get_by_id(self, tag_id: int) -> Tag | None:
        """Тег по идентификатору или None."""

        return await self.db.get(Tag, tag_id)

    async def get_by_ids(self, tag_ids: list[int]) -> list[Tag]:
        """Теги по списку идентификаторов. Если хотя бы один не найден — TagNotFoundError."""

        if not tag_ids:
            return []

        wanted_ids = set(tag_ids)
        stmt = select(Tag).where(Tag.id.in_(wanted_ids))
        result = await self.db.execute(stmt)
        tags = list(result.scalars().all())

        if len(tags) != len(wanted_ids):
            raise TagNotFoundError("Некоторые теги не найдены")

        return tags

    async def unique_slug(self, wanted: str) -> str:
        """Вернуть wanted, если такого slug нет, иначе добавить суффикс -2, -3, ..."""

        slug = wanted
        suffix = 2

        while True:
            stmt = select(Tag.id).where(Tag.slug == slug)

            taken = await self.db.scalar(stmt)
            if taken is None:
                return slug

            slug = f"{wanted}-{suffix}"
            suffix += 1

    async def add(self, tag: Tag) -> Tag:
        """Сохранить новый тег."""

        self.db.add(tag)
        await self.db.commit()
        await self.db.refresh(tag)

        return tag

    async def delete(self, tag: Tag) -> None:
        """Удалить тег. Со статей он снимается каскадом, сами статьи остаются."""

        await self.db.delete(tag)
        await self.db.commit()
