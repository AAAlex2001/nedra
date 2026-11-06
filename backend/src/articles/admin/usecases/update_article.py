"""Редактирование публикации."""

from datetime import UTC, datetime

from slugify import slugify
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.admin.schemas.update_article import (
    UpdateArticleRequest,
    UpdateArticleResponse,
)
from src.articles.exceptions import (
    ArticleConflictError,
    ArticleNotFoundError,
    TagNotFoundError,
)
from src.articles.models.article import Article
from src.articles.models.article_content import ArticleContent
from src.articles.options import ARTICLE_SLUG_MAX_LENGTH
from src.articles.prepared_content import PreparedContent
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
    ) -> UpdateArticleResponse:
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

        self._update_article_card(
            article=article,
            payload=payload,
        )
        self._update_article_content(
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

            response = UpdateArticleResponse.from_model(
                article=article,
                content=content,
                tags=tags,
            )
            await self.session.commit()
        except IntegrityError as error:
            await self.session.rollback()
            raise ArticleConflictError() from error

        return response

    @staticmethod
    def _update_article_card(
        *,
        article: Article,
        payload: UpdateArticleRequest,
    ) -> None:
        """Применить поля карточки."""

        if payload.title is not None:
            article.title = payload.title

        if payload.section is not None:
            article.section = payload.section

        if "description" in payload.model_fields_set:
            article.description = payload.description

        if "cover_image" in payload.model_fields_set:
            article.cover_image = payload.cover_image

        if payload.published is True and article.published_at is None:
            article.published_at = datetime.now(UTC)
        elif payload.published is False:
            article.published_at = None

        if payload.published_at is not None:
            article.published_at = payload.published_at

        article.updated_at = datetime.now(UTC)

    @staticmethod
    def _update_article_content(
        *,
        content: ArticleContent,
        payload: UpdateArticleRequest,
    ) -> None:
        """Применить текст и поисковое описание."""

        if payload.content is not None:
            prepared = PreparedContent.from_html(raw_html=payload.content)
            content.content = prepared.html
            content.toc = prepared.headings

        if payload.documents is not None:
            content.documents = [document.to_record() for document in payload.documents]

        if "seo_title" in payload.model_fields_set:
            content.seo_title = payload.seo_title

        if "seo_description" in payload.model_fields_set:
            content.seo_description = payload.seo_description

        if "seo_keywords" in payload.model_fields_set:
            content.seo_keywords = payload.seo_keywords
