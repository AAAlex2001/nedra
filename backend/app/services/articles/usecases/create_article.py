"""Сценарий создания статьи."""

from app.models.article import Article
from app.schemas.article import ArticleCreateSchema
from app.services.articles.content import make_slug, prepare_content
from app.services.articles.publishing import apply_published
from app.services.articles.repo import ArticleRepository
from app.services.articles.tags import TagRepository


class CreateArticleUseCase:
    """Очистить HTML, собрать оглавление, подобрать slug и сохранить."""

    def __init__(self, articles: ArticleRepository, tags: TagRepository) -> None:
        self.articles = articles
        self.tags = tags

    async def execute(self, data: ArticleCreateSchema) -> Article:
        """Создать статью. Бросает TagNotFoundError.

        Slug берётся из запроса или строится из заголовка; при совпадении
        с существующим получает числовой суффикс.
        Если передана published_at, она важнее флага published.
        """

        content, toc = prepare_content(data.content)
        wanted_slug = data.slug or make_slug(data.title)
        slug = await self.articles.unique_slug(wanted_slug)
        tags = await self.tags.get_by_ids(data.tag_ids)

        article = Article(
            slug=slug,
            section=data.section,
            title=data.title,
            description=data.description,
            cover_image=data.cover_image,
            content=content,
            toc=toc,
            seo_title=data.seo_title,
            seo_description=data.seo_description,
            seo_keywords=data.seo_keywords,
            tags=tags,
        )

        apply_published(article, data.published)
        if data.published_at is not None:
            article.published_at = data.published_at

        return await self.articles.add(article)
