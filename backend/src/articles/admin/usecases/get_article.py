"""Публикация для редактирования."""

from src.articles.admin.schemas.article import AdminArticleResponse
from src.articles.exceptions import ArticleNotFoundError
from src.articles.repositories.article_contents import ArticleContentRepository
from src.articles.repositories.articles import ArticleRepository
from src.articles.repositories.tags import TagRepository


class GetAdminArticleUseCase:
    """Просмотр статьи редактором."""

    def __init__(
        self,
        *,
        articles: ArticleRepository,
        contents: ArticleContentRepository,
        tags: TagRepository,
    ) -> None:
        """Публикации, содержимое и теги."""

        self.articles = articles
        self.contents = contents
        self.tags = tags

    async def execute(self, *, article_id: int) -> AdminArticleResponse:
        """Получить статью для редактирования."""

        article = await self.articles.get_by_id(article_id=article_id)
        content = await self.contents.get(article_id=article_id)

        if article is None or content is None:
            raise ArticleNotFoundError()

        tags_by_article = await self.tags.list_for_articles(article_ids={article_id})

        return AdminArticleResponse.from_article(
            article=article,
            content=content,
            tags=tags_by_article.get(article_id, []),
        )
