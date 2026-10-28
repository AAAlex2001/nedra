"""Каталог статей: стабильная пагинация и поиск по заголовку."""

import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models.article import Article, Tag, article_tags
from app.services.articles.repo import ArticleRepository, contains_pattern


class SessionAdapter:
    """Выполнить реальные запросы репозитория в изолированной SQLite БД."""

    def __init__(self, session: Session) -> None:
        self.session = session

    async def execute(self, statement):
        return self.session.execute(statement)

    async def scalar(self, statement):
        return self.session.scalar(statement)


def create_catalog_engine():
    """SQLite в памяти с таблицами статей и тегов."""

    engine = create_engine("sqlite://")
    for table in (Article.__table__, Tag.__table__, article_tags):
        table.create(engine)

    return engine


def test_equal_publication_dates_have_stable_pages():
    engine = create_catalog_engine()

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


def test_search_matches_title_case_insensitively():
    engine = create_catalog_engine()
    titles = ["Expert review deadline", "New EXPERT rules", "Audit checklist", "Draft expert notes"]

    with Session(engine) as session:
        published = datetime(2020, 1, 1, tzinfo=timezone.utc)
        for number, title in enumerate(titles, start=1):
            session.add(Article(
                id=number,
                slug=f"article-{number}",
                section="news",
                title=title,
                content="<p>Article</p>",
                published_at=None if number == 4 else published,
            ))
        session.commit()
        repo = ArticleRepository(SessionAdapter(session))

        found, total = asyncio.run(repo.list_published("news", None, 10, 0, "expert"))

        assert total == 2
        assert sorted(article.id for article in found) == [1, 2]
    engine.dispose()


def test_search_pattern_escapes_wildcards():
    assert contains_pattern("100%") == "%100\\%%"
    assert contains_pattern("snake_case") == "%snake\\_case%"
