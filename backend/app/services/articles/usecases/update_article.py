"""Сценарий частичного обновления статьи."""

from app.models.article import Article
from app.schemas.article import ArticleUpdateSchema
from app.services.articles.content import make_slug, prepare_content
from app.services.articles.publishing import apply_published
from app.services.articles.repo import ArticleRepository
from app.services.articles.tags import TagRepository


class UpdateArticleUseCase:
    """Изменить только те поля, которые пришли в запросе."""

    def __init__(self, articles: ArticleRepository, tags: TagRepository) -> None:
        self.articles = articles
        self.tags = tags

    async def execute(self, article: Article, data: ArticleUpdateSchema) -> Article:
        """Обновить статью. Бросает TagNotFoundError."""

        changes = data.model_dump(exclude_unset=True)

        if changes.get("title"):
            article.title = changes["title"]

        if changes.get("section"):
            article.section = changes["section"]

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
            article.slug = await self.articles.unique_slug(wanted, exclude_id=article.id)

        if "tag_ids" in changes:
            article.tags = await self.tags.get_by_ids(changes["tag_ids"] or [])

        if "published" in changes:
            apply_published(article, changes["published"])

        if changes.get("published_at") is not None:
            article.published_at = changes["published_at"]

        return await self.articles.save(article)
