"""Содержимое страниц статей."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.models.article_content import ArticleContent


class ArticleContentRepository:
    """Текст, оглавление и поисковые описания."""

    def __init__(self, *, session: AsyncSession) -> None:
        """Сессия базы данных."""

        self.session = session

    async def get(self, *, article_id: int) -> ArticleContent | None:
        """Получить содержимое статьи."""

        return await self.session.get(ArticleContent, article_id)

    async def save(self, *, content: ArticleContent) -> None:
        """Сохранить содержимое."""

        self.session.add(content)
        await self.session.flush()
