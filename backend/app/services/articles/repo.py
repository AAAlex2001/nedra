"""Репозиторий статей: только запросы к таблице articles."""

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article, Tag

PUBLISHED = and_(
    Article.published_at.is_not(None),
    Article.published_at <= func.now(),
)


class ArticleRepository:
    """Доступ к таблице articles. Сессию получает снаружи, коммитит сам."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_published(
        self, section: str | None, tag_slug: str | None, limit: int, offset: int
    ) -> tuple[list[Article], int]:
        """Опубликованные статьи, свежие первыми, и их общее количество для пагинации.

        Если передан section — только статьи этого раздела (blog или news).
        Если передан tag_slug — только статьи с этим тегом.
        """

        articles_stmt = select(Article).where(PUBLISHED)
        count_stmt = select(func.count()).select_from(Article).where(PUBLISHED)

        if section:
            articles_stmt = articles_stmt.where(Article.section == section)
            count_stmt = count_stmt.where(Article.section == section)

        if tag_slug:
            has_tag = Article.tags.any(Tag.slug == tag_slug)
            articles_stmt = articles_stmt.where(has_tag)
            count_stmt = count_stmt.where(has_tag)

        articles_stmt = (
            articles_stmt.order_by(Article.published_at.desc()).limit(limit).offset(offset)
        )

        result = await self.db.execute(articles_stmt)
        articles = list(result.scalars().all())

        total = await self.db.scalar(count_stmt)
        if total is None:
            total = 0

        return articles, total

    async def get_published(self, slug: str) -> Article | None:
        """Опубликованная статья по slug. Черновик считается ненайденным."""

        stmt = select(Article).where(Article.slug == slug, PUBLISHED)
        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_related(self, article: Article, limit: int) -> list[Article]:
        """Случайные опубликованные статьи того же раздела для блока «Смотрите также»."""

        stmt = (
            select(Article)
            .where(PUBLISHED, Article.section == article.section, Article.id != article.id)
            .order_by(func.random())
            .limit(limit)
        )
        result = await self.db.execute(stmt)

        return list(result.scalars().all())

    async def list_all(self, section: str | None) -> list[Article]:
        """Все статьи для админки, включая черновики, новые первыми."""

        stmt = select(Article).order_by(Article.created_at.desc())

        if section:
            stmt = stmt.where(Article.section == section)

        result = await self.db.execute(stmt)

        return list(result.scalars().all())

    async def get_by_id(self, article_id: int) -> Article | None:
        """Статья по идентификатору для админки, черновики тоже."""

        return await self.db.get(Article, article_id)

    async def unique_slug(self, wanted: str, exclude_id: int | None = None) -> str:
        """Вернуть wanted, если такого slug нет, иначе добавить суффикс -2, -3, ...

        exclude_id исключает саму редактируемую статью из проверки,
        чтобы сохранение без смены slug не давало ложного конфликта.
        """

        slug = wanted
        suffix = 2

        while True:
            stmt = select(Article.id).where(Article.slug == slug)
            if exclude_id is not None:
                stmt = stmt.where(Article.id != exclude_id)

            taken = await self.db.scalar(stmt)
            if taken is None:
                return slug

            slug = f"{wanted}-{suffix}"
            suffix += 1

    async def add(self, article: Article) -> Article:
        """Сохранить новую статью и вернуть её перечитанной из базы."""

        self.db.add(article)
        await self.db.commit()

        return await self.reload(article.id)

    async def save(self, article: Article) -> Article:
        """Сохранить изменения существующей статьи и вернуть её перечитанной."""

        await self.db.commit()

        return await self.reload(article.id)

    async def delete(self, article: Article) -> None:
        """Удалить статью. Связи с тегами, просмотры и реакции удаляет база каскадом."""

        await self.db.delete(article)
        await self.db.commit()

    async def reload(self, article_id: int) -> Article:
        """Перечитать статью из базы после записи.

        После commit колонки с onupdate и server_default помечены устаревшими,
        а ленивая подгрузка в async невозможна. populate_existing заставляет
        SQLAlchemy обновить объект в сессии свежими данными, включая теги.
        """

        stmt = (
            select(Article)
            .where(Article.id == article_id)
            .execution_options(populate_existing=True)
        )
        result = await self.db.execute(stmt)

        return result.scalar_one()
