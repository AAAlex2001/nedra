"""Редактирование публикации."""

from slugify import slugify
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.admin.article_changes import update_article_card, update_article_content
from src.articles.admin.schemas.article import AdminArticleResponse, UpdateArticleRequest
from src.articles.exceptions import ArticleConflictError, ArticleNotFoundError, TagNotFoundError
from src.articles.options import ARTICLE_SLUG_MAX_LENGTH
from src.articles.repositories.article_contents import ArticleContentRepository
from src.articles.repositories.articles import ArticleRepository
from src.articles.repositories.tags import TagRepository


class UpdateArticleUseCase:
    """Изменение существующей статьи."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        articles: ArticleRepository,
        contents: ArticleContentRepository,
        tags: TagRepository,
    ) -> None:
        """Публикации, содержимое и теги."""

        self.session = session
        self.articles = articles
        self.contents = contents
        self.tags = tags

    async def execute(
        self,
        *,
        article_id: int,
        payload: UpdateArticleRequest,
    ) -> AdminArticleResponse:
        """Сохранить изменения публикации."""

        article = await self.articles.get_for_update(article_id=article_id)
        content = await self.contents.get(article_id=article_id)

        if article is None or content is None:
            raise ArticleNotFoundError()

        tags_by_article = await self.tags.list_for_articles(article_ids={article_id})
        tags = tags_by_article.get(article_id, [])

        if payload.tag_ids is not None:
            tags = await self.tags.list_by_ids(tag_ids=set(payload.tag_ids))

            if len(tags) != len(set(payload.tag_ids)):
                raise TagNotFoundError()

        update_article_card(
            article=article,
            payload=payload,
        )
        update_article_content(
            content=content,
            payload=payload,
        )

        if "slug" in payload.model_fields_set:
            wanted_slug = (
                payload.slug
                or slugify(article.title, max_length=ARTICLE_SLUG_MAX_LENGTH)
                or "article"
            )
            article.slug = await self.articles.find_free_slug(
                wanted_slug=wanted_slug,
                exclude_id=article_id,
            )

        try:
            await self.articles.save(article=article)
            await self.contents.save(content=content)

            if payload.tag_ids is not None:
                await self.tags.replace_for_article(
                    article_id=article_id,
                    tag_ids=set(payload.tag_ids),
                )

            response = AdminArticleResponse.from_article(
                article=article,
                content=content,
                tags=tags,
            )
            await self.session.commit()
        except IntegrityError as error:
            await self.session.rollback()
            raise ArticleConflictError() from error

        return response
