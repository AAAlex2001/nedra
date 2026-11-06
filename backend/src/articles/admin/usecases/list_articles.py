"""Редакторский список публикаций."""

from src.articles.admin.schemas.list_articles import (
    ArticleListItem,
    ListArticlesRequest,
    ListArticlesResponse,
)
from src.articles.repositories.articles import ArticleRepository
from src.articles.repositories.tags import TagRepository


class ListAdminArticlesUseCase:
    """Поиск публикаций, включая черновики."""

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
        """Получить страницу редакторского списка."""

        articles, total = await self.articles.list_admin(
            section=payload.section,
            search=payload.search.strip() if payload.search else None,
            sort=payload.sort,
            limit=payload.limit,
            offset=payload.offset,
        )
        tags_by_article = await self.tags.list_for_articles(
            article_ids={article.id for article in articles},
        )

        return ListArticlesResponse(
            articles=[
                ArticleListItem.from_model(
                    article=article,
                    tags=tags_by_article.get(article.id, []),
                )
                for article in articles
            ],
            total=total,
        )
