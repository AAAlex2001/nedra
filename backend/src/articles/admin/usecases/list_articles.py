"""Редакторский список публикаций."""

from src.articles.admin.schemas.article import AdminArticleCardResponse, AdminArticleListResponse
from src.articles.enums import AdminArticleSort, ArticleSection
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
        section: ArticleSection | None,
        search: str | None,
        sort: AdminArticleSort,
        limit: int,
        offset: int,
    ) -> AdminArticleListResponse:
        """Получить страницу редакторского списка."""

        articles, total = await self.articles.list_admin(
            section=section,
            search=search.strip() if search else None,
            sort=sort,
            limit=limit,
            offset=offset,
        )
        tags_by_article = await self.tags.list_for_articles(
            article_ids={article.id for article in articles},
        )

        return AdminArticleListResponse(
            articles=[
                AdminArticleCardResponse.from_model(
                    article=article,
                    tags=tags_by_article.get(article.id, []),
                )
                for article in articles
            ],
            total=total,
        )
