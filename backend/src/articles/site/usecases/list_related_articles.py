"""Похожие публикации."""

from src.articles.exceptions import ArticleNotFoundError
from src.articles.repositories.articles import ArticleRepository
from src.articles.repositories.tags import TagRepository
from src.articles.site.schemas.related_articles import (
    RelatedArticleResponse,
    RelatedArticlesRequest,
)


class ListRelatedArticlesUseCase:
    """Другие статьи выбранного раздела."""

    def __init__(
        self,
        *,
        articles: ArticleRepository,
        tags: TagRepository,
    ) -> None:
        """Публикации и теги."""

        self.articles = articles
        self.tags = tags

    async def execute(
        self,
        *,
        payload: RelatedArticlesRequest,
    ) -> list[RelatedArticleResponse]:
        """Подобрать публикации для чтения."""

        article = await self.articles.get_published(slug=payload.slug)

        if article is None:
            raise ArticleNotFoundError()

        related = await self.articles.list_related(
            article=article,
            limit=payload.limit,
        )
        tags_by_article = await self.tags.list_for_articles(
            article_ids={item.id for item in related},
        )

        return [
            RelatedArticleResponse.from_model(
                article=item,
                tags=tags_by_article.get(item.id, []),
            )
            for item in related
        ]
