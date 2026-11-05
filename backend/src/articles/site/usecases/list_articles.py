"""Список опубликованных статей."""

from src.articles.enums import ArticleSection, ArticleSort
from src.articles.repositories.articles import ArticleRepository
from src.articles.repositories.tags import TagRepository
from src.articles.schemas.article import ArticleCardResponse, ArticleListResponse


class ListArticlesUseCase:
    """Страница новостей или блога."""

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
        section: ArticleSection | None,
        tag_slug: str | None,
        search: str | None,
        sort: ArticleSort,
        limit: int,
        offset: int,
    ) -> ArticleListResponse:
        """Получить отфильтрованные публикации."""

        articles, total = await self.articles.list_published(
            section=section,
            tag_slug=tag_slug,
            search=search.strip() if search else None,
            sort=sort,
            limit=limit,
            offset=offset,
        )
        tags_by_article = await self.tags.list_for_articles(
            article_ids={article.id for article in articles},
        )

        return ArticleListResponse(
            articles=[
                ArticleCardResponse.from_model(
                    article=article,
                    tags=tags_by_article.get(article.id, []),
                )
                for article in articles
            ],
            total=total,
        )
