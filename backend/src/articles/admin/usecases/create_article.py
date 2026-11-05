"""Создание публикации."""

from datetime import UTC, datetime

from slugify import slugify
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.admin.schemas.article import AdminArticleResponse, CreateArticleRequest
from src.articles.content import prepare_content
from src.articles.exceptions import ArticleConflictError, TagNotFoundError
from src.articles.models.article import Article
from src.articles.models.article_content import ArticleContent
from src.articles.options import ARTICLE_SLUG_MAX_LENGTH
from src.articles.repositories.article_contents import ArticleContentRepository
from src.articles.repositories.articles import ArticleRepository
from src.articles.repositories.tags import TagRepository


class CreateArticleUseCase:
    """Новая статья редактора."""

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

    async def execute(self, *, payload: CreateArticleRequest) -> AdminArticleResponse:
        """Сохранить новую публикацию."""

        tag_ids = set(payload.tag_ids)
        tags = await self.tags.list_by_ids(tag_ids=tag_ids)

        if len(tags) != len(tag_ids):
            raise TagNotFoundError()

        wanted_slug = (
            payload.slug or slugify(payload.title, max_length=ARTICLE_SLUG_MAX_LENGTH) or "article"
        )
        slug = await self.articles.find_free_slug(wanted_slug=wanted_slug)
        published_at = payload.published_at

        if published_at is None and payload.published:
            published_at = datetime.now(UTC)

        article = Article(
            title=payload.title,
            slug=slug,
            section=payload.section,
            description=payload.description,
            cover_image=payload.cover_image,
            published_at=published_at,
        )
        prepared = prepare_content(raw_html=payload.content)

        try:
            await self.articles.save(article=article)
            content = ArticleContent(
                article_id=article.id,
                content=prepared.html,
                toc=prepared.headings,
                documents=[document.to_record() for document in payload.documents],
                seo_title=payload.seo_title,
                seo_description=payload.seo_description,
                seo_keywords=payload.seo_keywords,
            )
            await self.contents.save(content=content)
            await self.tags.replace_for_article(
                article_id=article.id,
                tag_ids=tag_ids,
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
