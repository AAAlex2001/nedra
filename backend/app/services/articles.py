"""Сервис статей блога: публичное чтение, просмотры, реакции, админские операции."""

from dataclasses import dataclass

from sqlalchemy import and_, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.articles import Article, ArticleReaction, ArticleView, Tag
from app.schemas.articles import ArticleCreateSchema, ArticleUpdateSchema
from app.services.content import make_slug, prepare_content
from app.services.exceptions import ArticleNotFoundError, TagNotFoundError

LIKE = 1
DISLIKE = -1

PUBLISHED = and_(
    Article.published_at.is_not(None),
    Article.published_at <= func.now(),
)


@dataclass(frozen=True)
class ArticleStats:
    """Счётчики статьи и реакция текущего посетителя."""

    views_count: int
    likes_count: int
    dislikes_count: int
    my_reaction: int | None


class ArticleService:
    """Работа со статьями. Сессию получает снаружи, коммитит сам."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_published(
        self, tag_slug: str | None, limit: int, offset: int
    ) -> tuple[list[Article], int]:
        """Опубликованные статьи, свежие первыми, и их общее количество для пагинации.

        Если передан tag_slug — только статьи с этим тегом.
        """

        articles_stmt = select(Article).where(PUBLISHED)
        count_stmt = select(func.count()).select_from(Article).where(PUBLISHED)

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

    async def get_published(self, slug: str) -> Article:
        """Опубликованная статья по slug. Черновик считается ненайденным."""

        stmt = select(Article).where(Article.slug == slug, PUBLISHED)
        result = await self.db.execute(stmt)
        article = result.scalar_one_or_none()

        if article is None:
            raise ArticleNotFoundError(f"Статья «{slug}» не найдена")

        return article

    async def get_related(self, article: Article, limit: int) -> list[Article]:
        """Случайные опубликованные статьи для блока «Смотрите также», кроме текущей."""

        stmt = (
            select(Article)
            .where(PUBLISHED, Article.id != article.id)
            .order_by(func.random())
            .limit(limit)
        )

        result = await self.db.execute(stmt)

        return list(result.scalars().all())

    async def list_tags(self) -> list[Tag]:
        """Все теги по алфавиту."""

        stmt = select(Tag).order_by(Tag.title)

        result = await self.db.execute(stmt)

        return list(result.scalars().all())

    async def register_view(self, article: Article, visitor_id: str) -> None:
        """Засчитать просмотр статьи.

        Один посетитель учитывается один раз: это гарантирует составной
        первичный ключ (article_id, visitor_id). Если два запроса пришли
        одновременно и оба прошли проверку, второй упадёт на IntegrityError —
        тогда просмотр уже учтён и делать ничего не нужно.
        """

        already_viewed = await self.db.get(ArticleView, (article.id, visitor_id))
        if already_viewed is not None:
            return

        self.db.add(ArticleView(article_id=article.id, visitor_id=visitor_id))

        try:
            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            return

        await self.db.execute(
            update(Article)
            .where(Article.id == article.id)
            .values(views_count=Article.views_count + 1)
        )
        await self.db.commit()

    async def set_reaction(self, article: Article, visitor_id: str, value: int) -> None:
        """Поставить лайк (1) или дизлайк (-1).

        Повторный клик тем же значением ничего не меняет.
        Другое значение переключает реакцию и переносит единицу между счётчиками.
        """

        reaction = await self.db.get(ArticleReaction, (article.id, visitor_id))

        if reaction is None:
            await self.create_reaction(article, visitor_id, value)
        elif reaction.value != value:
            await self.switch_reaction(article, reaction, value)

    async def remove_reaction(self, article: Article, visitor_id: str) -> None:
        """Снять реакцию посетителя, если она была."""

        reaction = await self.db.get(ArticleReaction, (article.id, visitor_id))
        if reaction is None:
            return

        if reaction.value == LIKE:
            await self.update_counters(article.id, likes=-1)
        else:
            await self.update_counters(article.id, dislikes=-1)

        await self.db.delete(reaction)
        await self.db.commit()

    async def get_stats(self, article_id: int, visitor_id: str) -> ArticleStats:
        """Актуальные счётчики статьи и реакция этого посетителя.

        Читает колонки напрямую из базы, а не из объекта в сессии:
        после массового UPDATE значения в объекте могут быть устаревшими.
        """

        stmt = select(
            Article.views_count, Article.likes_count, Article.dislikes_count
        ).where(Article.id == article_id)
        result = await self.db.execute(stmt)
        counters = result.one()

        reaction = await self.db.get(ArticleReaction, (article_id, visitor_id))
        my_reaction = None
        if reaction is not None:
            my_reaction = reaction.value

        return ArticleStats(
            views_count=counters.views_count,
            likes_count=counters.likes_count,
            dislikes_count=counters.dislikes_count,
            my_reaction=my_reaction,
        )

    async def list_all(self) -> list[Article]:
        """Все статьи для админки, включая черновики, новые первыми."""

        stmt = select(Article).order_by(Article.created_at.desc())

        result = await self.db.execute(stmt)

        return list(result.scalars().all())

    async def get_by_id(self, article_id: int) -> Article:
        """Статья по идентификатору для админки, черновики тоже."""

        article = await self.db.get(Article, article_id)

        if article is None:
            raise ArticleNotFoundError(f"Статья с ID {article_id} не найдена")

        return article

    async def create(self, data: ArticleCreateSchema) -> Article:
        """Создать статью.

        HTML очищается, оглавление собирается из заголовков H2.
        Slug берётся из запроса или строится из заголовка; при совпадении
        с существующим получает числовой суффикс.
        """

        content, toc = prepare_content(data.content)
        wanted_slug = data.slug or make_slug(data.title)
        slug = await self.unique_slug(wanted_slug)
        tags = await self.tags_by_ids(data.tag_ids)

        article = Article(
            slug=slug,
            title=data.title,
            description=data.description,
            cover_image=data.cover_image,
            content=content,
            toc=toc,
            seo_title=data.seo_title,
            seo_description=data.seo_description,
            seo_keywords=data.seo_keywords,
            published_at=func.now() if data.published else None,
            tags=tags,
        )

        self.db.add(article)
        await self.db.commit()

        return await self.reload(article.id)

    async def update(self, article: Article, data: ArticleUpdateSchema) -> Article:
        """Частичное обновление: меняются только поля, которые пришли в запросе."""

        changes = data.model_dump(exclude_unset=True)

        if changes.get("title"):
            article.title = changes["title"]

        if "description" in changes:
            article.description = changes["description"]

        if "cover_image" in changes:
            article.cover_image = changes["cover_image"]

        if "seo_title" in changes:
            article.seo_title = changes["seo_title"]

        if "seo_description" in changes:
            article.seo_description = changes["seo_description"]

        if "seo_keywords" in changes:
            article.seo_keywords = changes["seo_keywords"]

        if changes.get("content"):
            article.content, article.toc = prepare_content(changes["content"])

        if "slug" in changes:
            wanted = changes["slug"] or make_slug(article.title)
            article.slug = await self.unique_slug(wanted, exclude_id=article.id)

        if "tag_ids" in changes:
            article.tags = await self.tags_by_ids(changes["tag_ids"] or [])

        if "published" in changes:
            self.apply_published(article, changes["published"])

        await self.db.commit()

        return await self.reload(article.id)

    async def delete(self, article: Article) -> None:
        """Удалить статью. Связи с тегами, просмотры и реакции удаляет база каскадом."""

        await self.db.delete(article)
        await self.db.commit()

    async def create_tag(self, title: str) -> Tag:
        """Создать тег. Slug строится из названия и при совпадении получает суффикс."""

        wanted_slug = make_slug(title, max_length=90)
        slug = await self.unique_tag_slug(wanted_slug)

        tag = Tag(slug=slug, title=title)
        self.db.add(tag)
        await self.db.commit()
        await self.db.refresh(tag)

        return tag

    async def delete_tag(self, tag_id: int) -> None:
        """Удалить тег. Со статей он снимается каскадом, сами статьи остаются."""

        tag = await self.db.get(Tag, tag_id)

        if tag is None:
            raise TagNotFoundError(f"Тег с ID {tag_id} не найден")

        await self.db.delete(tag)
        await self.db.commit()

    async def create_reaction(self, article: Article, visitor_id: str, value: int) -> None:
        """Первая реакция посетителя: запись в таблицу плюс единица в нужный счётчик."""

        self.db.add(
            ArticleReaction(article_id=article.id, visitor_id=visitor_id, value=value)
        )

        try:
            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            return

        if value == LIKE:
            await self.update_counters(article.id, likes=1)
        else:
            await self.update_counters(article.id, dislikes=1)

        await self.db.commit()

    async def switch_reaction(
        self, article: Article, reaction: ArticleReaction, value: int
    ) -> None:
        """Смена лайка на дизлайк или наоборот: единица переносится между счётчиками."""

        reaction.value = value

        if value == LIKE:
            await self.update_counters(article.id, likes=1, dislikes=-1)
        else:
            await self.update_counters(article.id, likes=-1, dislikes=1)

        await self.db.commit()

    async def update_counters(self, article_id: int, likes: int = 0, dislikes: int = 0) -> None:
        """Изменить счётчики лайков и дизлайков на указанные величины.

        Арифметика выполняется в базе, а не в Python, чтобы параллельные
        запросы не затирали обновления друг друга.
        """

        await self.db.execute(
            update(Article)
            .where(Article.id == article_id)
            .values(
                likes_count=Article.likes_count + likes,
                dislikes_count=Article.dislikes_count + dislikes,
            )
        )

    @staticmethod
    def apply_published(article: Article, published: bool | None) -> None:
        """Опубликовать статью, если она ещё не опубликована, или снять с публикации.

        Дату публикации ставит база, чтобы она совпадала по часам с created_at.
        """

        if published and article.published_at is None:
            article.published_at = func.now()
        elif published is False:
            article.published_at = None

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

    async def unique_tag_slug(self, wanted: str) -> str:
        """То же, что unique_slug, но для тегов."""

        slug = wanted
        suffix = 2

        while True:
            stmt = select(Tag.id).where(Tag.slug == slug)

            taken = await self.db.scalar(stmt)
            if taken is None:
                return slug

            slug = f"{wanted}-{suffix}"
            suffix += 1

    async def tags_by_ids(self, tag_ids: list[int]) -> list[Tag]:
        """Теги по списку идентификаторов. Если хотя бы один не найден — ошибка."""

        if not tag_ids:
            return []

        wanted_ids = set(tag_ids)
        stmt = select(Tag).where(Tag.id.in_(wanted_ids))
        result = await self.db.execute(stmt)
        tags = list(result.scalars().all())

        if len(tags) != len(wanted_ids):
            raise TagNotFoundError("Некоторые теги не найдены")

        return tags
