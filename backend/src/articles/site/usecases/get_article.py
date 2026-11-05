"""Просмотр публикации."""

from src.articles.exceptions import ArticleNotFoundError
from src.articles.repositories.article_contents import ArticleContentRepository
from src.articles.repositories.articles import ArticleRepository
from src.articles.repositories.tags import TagRepository
from src.articles.schemas.article import ArticleResponse


class GetArticleUseCase:
    """Текст опубликованной статьи."""

    def __init__(
        self,
        *,
        articles: ArticleRepository,
        contents: ArticleContentRepository,
        tags: TagRepository,
    ) -> None:
        """Карточки, тексты и теги."""

        self.articles = articles
        self.contents = contents
        self.tags = tags

    async def execute(self, *, slug: str) -> ArticleResponse:
        """Открыть публикацию."""

        article = await self.articles.get_published(slug=slug)

        if article is None:
            raise ArticleNotFoundError()

        content = await self.contents.get(article_id=article.id)

        if content is None:
            raise ArticleNotFoundError()

        tags_by_article = await self.tags.list_for_articles(article_ids={article.id})

        return ArticleResponse.from_article(
            article=article,
            content=content,
            tags=tags_by_article.get(article.id, []),
        )
