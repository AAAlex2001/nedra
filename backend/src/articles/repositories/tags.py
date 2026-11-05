"""Теги и привязки к публикациям."""

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.enums import ArticleSection
from src.articles.models.article import Article
from src.articles.models.article_tag import ArticleTag
from src.articles.models.tag import Tag


class TagRepository:
    """Поиск и сохранение тегов."""

    def __init__(self, *, session: AsyncSession) -> None:
        """Сессия базы данных."""

        self.session = session

    async def list_all(self, *, section: ArticleSection | None = None) -> list[Tag]:
        """Получить теги выбранного раздела."""

        statement = select(Tag).order_by(Tag.title, Tag.id)

        if section is not None:
            published_tags = (
                select(ArticleTag.tag_id)
                .join(
                    Article,
                    Article.id == ArticleTag.article_id,
                )
                .where(Article.section == section, Article.published_at <= func.now())
            )
            statement = statement.where(Tag.id.in_(published_tags))

        query_result = await self.session.scalars(statement)
        return list(query_result)

    async def list_by_ids(self, *, tag_ids: set[int]) -> list[Tag]:
        """Найти выбранные теги."""

        if not tag_ids:
            return []

        statement = select(Tag).where(Tag.id.in_(tag_ids)).order_by(Tag.title, Tag.id)
        query_result = await self.session.scalars(statement)
        return list(query_result)

    async def list_for_articles(self, *, article_ids: set[int]) -> dict[int, list[Tag]]:
        """Получить теги для страницы статей."""

        if not article_ids:
            return {}

        statement = (
            select(ArticleTag.article_id, Tag)
            .join(
                Tag,
                Tag.id == ArticleTag.tag_id,
            )
            .where(ArticleTag.article_id.in_(article_ids))
            .order_by(Tag.title, Tag.id)
        )
        query_result = await self.session.execute(statement)
        tags_by_article = {}

        for article_id, tag in query_result:
            if article_id not in tags_by_article:
                tags_by_article[article_id] = []

            tags_by_article[article_id].append(tag)

        return tags_by_article

    async def replace_for_article(
        self,
        *,
        article_id: int,
        tag_ids: set[int],
    ) -> None:
        """Заменить теги статьи."""

        await self.session.execute(
            delete(ArticleTag).where(ArticleTag.article_id == article_id),
        )

        for tag_id in sorted(tag_ids):
            self.session.add(
                ArticleTag(
                    article_id=article_id,
                    tag_id=tag_id,
                )
            )

        await self.session.flush()

    async def get_by_id(self, *, tag_id: int) -> Tag | None:
        """Найти тег."""

        return await self.session.get(Tag, tag_id)

    async def get_by_slug(self, *, slug: str) -> Tag | None:
        """Найти тег по адресу."""

        return await self.session.scalar(select(Tag).where(Tag.slug == slug))

    async def save(self, *, tag: Tag) -> None:
        """Сохранить тег."""

        self.session.add(tag)
        await self.session.flush()

    async def delete(self, *, tag: Tag) -> None:
        """Удалить тег и его привязки."""

        await self.session.delete(tag)
        await self.session.flush()
