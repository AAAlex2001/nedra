"""Список опубликованных статей."""

from src.articles.repositories.articles import ArticleRepository
from src.articles.repositories.tags import TagRepository
from src.articles.schemas.article import ArticleCardResponse
from src.articles.site.schemas.list_articles import ListArticlesRequest, ListArticlesResponse


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
        payload: ListArticlesRequest,
    ) -> ListArticlesResponse:
        """Получить отфильтрованные публикации."""

        articles, total = await self.articles.list_published(
            section=payload.section,
            tag_slug=payload.tag,
            search=payload.q.strip() if payload.q else None,
            sort=payload.sort,
            limit=payload.limit,
            offset=payload.offset,
        )
        tags_by_article = await self.tags.list_for_articles(
            article_ids={article.id for article in articles},
        )

        return ListArticlesResponse(
            articles=[
                ArticleCardResponse.from_model(
                    article=article,
                    tags=tags_by_article.get(article.id, []),
                )
                for article in articles
            ],
            total=total,
        )
