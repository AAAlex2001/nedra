"""Статьи с одинаковой датой не должны теряться между страницами каталога."""

import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models.article import Article, Tag, article_tags
from app.services.articles.repo import ArticleRepository


class SessionAdapter:
    """Выполнить реальные запросы репозитория в изолированной SQLite БД."""

    def __init__(self, session: Session) -> None:
        self.session = session

    async def execute(self, statement):
        return self.session.execute(statement)

    async def scalar(self, statement):
        return self.session.scalar(statement)


def test_equal_publication_dates_have_stable_pages():
    engine = create_engine("sqlite://")
    for table in (Article.__table__, Tag.__table__, article_tags):
        table.create(engine)

    with Session(engine) as session:
        published = datetime(2020, 1, 1, tzinfo=timezone.utc)
        for number in range(1, 8):
            session.add(Article(
                id=number,
                slug=f"article-{number}",
                section="news",
                title=f"Article {number}",
                content="<p>Article</p>",
                published_at=(
                    published if number <= 5 else
                    datetime.now(timezone.utc) + timedelta(days=30) if number == 6 else None
                ),
            ))
        session.commit()
        repo = ArticleRepository(SessionAdapter(session))

        async def read_pages():
            return [await repo.list_published("news", None, 2, offset) for offset in (0, 2, 4)]

        pages = asyncio.run(read_pages())
        assert [total for _, total in pages] == [5, 5, 5]
        assert [[article.id for article in articles] for articles, _ in pages] == [
            [5, 4], [3, 2], [1],
        ]
    engine.dispose()
