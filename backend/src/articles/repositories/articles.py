"""Поиск и сохранение карточек публикаций."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.enums import AdminArticleSort, ArticleSection, ArticleSort
from src.articles.models.article import Article
from src.articles.models.article_tag import ArticleTag
from src.articles.models.tag import Tag
from src.articles.options import ADMIN_ARTICLE_ORDER, PUBLISHED_ARTICLE_ORDER


class ArticleRepository:
    """Карточки статей без содержимого страницы."""

    def __init__(self, *, session: AsyncSession) -> None:
        """Сессия базы данных."""

        self.session = session

    async def list_published(
        self,
        *,
        section: ArticleSection | None,
        tag_slug: str | None,
        search: str | None,
        sort: ArticleSort,
        limit: int,
        offset: int,
    ) -> tuple[list[Article], int]:
        """Получить страницу опубликованных статей."""

        statement = select(Article).where(Article.published_at <= func.now())

        if section is not None:
            statement = statement.where(Article.section == section)

        if tag_slug:
            tagged_articles = (
                select(ArticleTag.article_id)
                .join(
                    Tag,
                    Tag.id == ArticleTag.tag_id,
                )
                .where(Tag.slug == tag_slug)
            )
            statement = statement.where(Article.id.in_(tagged_articles))

        if search:
            statement = statement.where(Article.title.icontains(search, autoescape=True))

        count_statement = select(func.count()).select_from(statement.subquery())
        total = await self.session.scalar(count_statement)
        statement = (
            statement.order_by(
                PUBLISHED_ARTICLE_ORDER[sort],
                Article.published_at.desc(),
                Article.id.desc(),
            )
            .limit(limit)
            .offset(offset)
        )
        query_result = await self.session.scalars(statement)

        return list(query_result), total or 0

    async def list_admin(
        self,
        *,
        section: ArticleSection | None,
        search: str | None,
        sort: AdminArticleSort,
        limit: int,
        offset: int,
    ) -> tuple[list[Article], int]:
        """Получить страницу редакторского списка."""

        statement = select(Article)

        if section is not None:
            statement = statement.where(Article.section == section)

        if search:
            statement = statement.where(Article.title.icontains(search, autoescape=True))

        total = await self.session.scalar(
            select(func.count()).select_from(statement.subquery()),
        )
        statement = (
            statement.order_by(
                ADMIN_ARTICLE_ORDER[sort],
                Article.created_at.desc(),
                Article.id.desc(),
            )
            .limit(limit)
            .offset(offset)
        )
        query_result = await self.session.scalars(statement)

        return list(query_result), total or 0

    async def get_published(self, *, slug: str) -> Article | None:
        """Найти опубликованную статью."""

        statement = select(Article).where(
            Article.slug == slug,
            Article.published_at <= func.now(),
        )
        return await self.session.scalar(statement)

    async def get_published_for_update(self, *, slug: str) -> Article | None:
        """Получить публикацию для изменения счётчиков."""

        statement = (
            select(Article)
            .where(
                Article.slug == slug,
                Article.published_at <= func.now(),
            )
            .with_for_update()
        )
        return await self.session.scalar(statement)

    async def get_by_id(self, *, article_id: int) -> Article | None:
        """Найти статью, включая черновик."""

        return await self.session.get(Article, article_id)

    async def get_for_update(self, *, article_id: int) -> Article | None:
        """Получить статью для редактирования."""

        statement = select(Article).where(Article.id == article_id).with_for_update()
        return await self.session.scalar(statement)

    async def list_related(
        self,
        *,
        article: Article,
        limit: int,
    ) -> list[Article]:
        """Подобрать другие публикации раздела."""

        statement = (
            select(Article)
            .where(
                Article.section == article.section,
                Article.id != article.id,
                Article.published_at <= func.now(),
            )
            .order_by(func.random())
            .limit(limit)
        )
        query_result = await self.session.scalars(statement)

        return list(query_result)

    async def find_free_slug(
        self,
        *,
        wanted_slug: str,
        exclude_id: int | None = None,
    ) -> str:
        """Подобрать свободный адрес."""

        candidate = wanted_slug
        suffix = 2

        while True:
            statement = select(Article.id).where(Article.slug == candidate)

            if exclude_id is not None:
                statement = statement.where(Article.id != exclude_id)

            if await self.session.scalar(statement) is None:
                return candidate

            suffix_text = f"-{suffix}"
            candidate = wanted_slug[: 255 - len(suffix_text)] + suffix_text
            suffix += 1

    async def save(self, *, article: Article) -> None:
        """Сохранить карточку."""

        self.session.add(article)
        await self.session.flush()

    async def delete(self, *, article: Article) -> None:
        """Удалить публикацию и связанные записи."""

        await self.session.delete(article)
        await self.session.flush()
