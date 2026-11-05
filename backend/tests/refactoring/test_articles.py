"""Публикации, сортировки и реакции нового API."""

import asyncio
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.articles.models.article import Article
from src.articles.models.article_content import ArticleContent
from src.articles.models.article_reaction import ArticleReaction
from src.articles.models.article_tag import ArticleTag
from src.articles.models.article_view import ArticleView
from src.articles.models.tag import Tag
from src.core.settings import Settings
from src.main import create_app


@pytest.mark.parametrize("section", ["news", "blog"])
@pytest.mark.parametrize(
    "sort, expected_ids",
    [
        ("newest", [4, 2, 3, 1]),
        ("oldest", [1, 3, 4, 2]),
        ("views_desc", [1, 3, 4, 2]),
        ("views_asc", [4, 2, 3, 1]),
        ("likes_desc", [4, 2, 1, 3]),
        ("likes_asc", [3, 1, 4, 2]),
        ("dislikes_desc", [3, 1, 4, 2]),
        ("dislikes_asc", [4, 2, 1, 3]),
    ],
)
async def test_catalog_sorting(
    session_factory: async_sessionmaker,
    settings: Settings,
    section: str,
    sort: str,
    expected_ids: list[int],
) -> None:
    """Сортировать до пагинации, сохраняя фильтры."""

    async with session_factory() as session:
        tag = Tag(slug="safety", title="Безопасность")
        session.add(tag)
        await session.flush()

        for number, day, views, likes, dislikes in [
            (1, 1, 30, 5, 2),
            (2, 3, 10, 9, 1),
            (3, 2, 20, 1, 7),
            (4, 3, 10, 9, 1),
        ]:
            article = Article(
                slug=f"review-{number}",
                section=section,
                title=f"Review {number}",
                published_at=datetime(2020, 1, day, tzinfo=UTC),
                views_count=views,
                likes_count=likes,
                dislikes_count=dislikes,
            )
            session.add(article)
            await session.flush()
            session.add(ArticleTag(article_id=number, tag_id=tag.id))

        session.add_all(
            [
                Article(
                    slug="excluded",
                    section=section,
                    title="Other",
                    published_at=datetime(2020, 1, 4, tzinfo=UTC),
                ),
                Article(slug="draft", section=section, title="Review draft"),
                Article(
                    slug="future",
                    section=section,
                    title="Review future",
                    published_at=datetime(2099, 1, 1, tzinfo=UTC),
                ),
            ]
        )
        await session.commit()

    app = create_app(settings=settings)
    app.state.session_factory = session_factory
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        pages = []
        for offset in (0, 2):
            response = await client.get(
                "/api/v1/articles",
                params={
                    "section": section,
                    "sort": sort,
                    "tag": "safety",
                    "q": "REVIEW",
                    "limit": 2,
                    "offset": offset,
                },
            )
            assert response.status_code == 200, response.text
            assert response.json()["total"] == 4
            pages.extend(response.json()["articles"])
        assert [article["slug"] for article in pages] == [
            f"review-{number}" for number in expected_ids
        ]
        assert all(
            article["tags"] == [{"slug": "safety", "title": "Безопасность"}] for article in pages
        )
        assert (await client.get("/api/v1/articles/draft")).status_code == 404
        assert (await client.get("/api/v1/articles/future")).status_code == 404
        assert (await client.get("/api/v1/articles", params={"sort": "invalid"})).status_code == 422
        assert (await client.get("/api/v1/articles", params={"q": "%"})).json()["total"] == 0


async def test_editor_and_concurrent_interactions(
    session_factory: async_sessionmaker,
    settings: Settings,
    tmp_path: Path,
) -> None:
    """Редактировать статью и учитывать действия ровно один раз."""

    settings.admin_api_token = "test-admin"
    settings.media_dir = tmp_path
    app = create_app(settings=settings)
    app.state.session_factory = session_factory
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        assert (await client.get("/api/v1/admin/articles")).status_code == 401
        client.headers["X-Admin-Token"] = settings.admin_api_token
        tag = (await client.post("/api/v1/admin/tags", json={"title": "Атомная лицензия"})).json()
        uploaded = await client.post(
            "/api/v1/admin/uploads/documents",
            files={
                "file": ("test.pdf", b"%PDF-1.4\n%%EOF", "application/pdf"),
            },
        )
        assert uploaded.status_code == 201, uploaded.text
        assert (
            await client.post(
                "/api/v1/admin/uploads",
                files={
                    "file": ("fake.png", b"not an image", "image/png"),
                },
            )
        ).status_code == 422
        created = await client.post(
            "/api/v1/admin/articles",
            json={
                "title": "Новая статья",
                "section": "news",
                "published": True,
                "content": '<script>alert(1)</script><h2>Заголовок</h2><h2>Заголовок</h2><p onclick="bad()">Текст</p>',
                "tag_ids": [tag["id"]],
                "documents": [{"title": "Документ", "url": uploaded.json()["url"]}],
                "seo_title": "Поисковый заголовок",
            },
        )
        assert created.status_code == 201, created.text
        article = created.json()
        article_id = article["id"]
        url = f"/api/v1/articles/{article['slug']}"
        page = (await client.get(url)).json()
        assert "script" not in page["content"] and "onclick" not in page["content"]
        assert [heading["id"] for heading in page["toc"]] == ["zagolovok", "zagolovok-2"]
        assert page["documents"][0]["kind"] == "pdf"
        assert page["seo_title"] == "Поисковый заголовок"
        changed_at = page["updated_at"]
        client.cookies.set("visitor_id", str(uuid4()))
        viewed = await asyncio.gather(*[client.post(f"{url}/view") for _ in range(4)])
        assert all(response.json()["views_count"] == 1 for response in viewed)
        liked = await asyncio.gather(
            *[client.put(f"{url}/reaction", json={"value": 1}) for _ in range(4)]
        )
        assert all(response.json()["likes_count"] == 1 for response in liked)
        disliked = await client.put(f"{url}/reaction", json={"value": -1})
        assert disliked.json() == {
            "views_count": 1,
            "likes_count": 0,
            "dislikes_count": 1,
            "my_reaction": -1,
        }
        removed = await asyncio.gather(*[client.delete(f"{url}/reaction") for _ in range(4)])
        assert all(response.json()["dislikes_count"] == 0 for response in removed)
        assert (await client.get(url)).json()["updated_at"] == changed_at
        assert (await client.put(f"{url}/reaction", json={"value": 0})).status_code == 422

        changed = await client.patch(
            f"/api/v1/admin/articles/{article_id}",
            json={
                "title": "Обновлённая статья",
                "tag_ids": [],
                "seo_title": None,
            },
        )
        assert changed.status_code == 200, changed.text
        assert changed.json()["tags"] == []
        assert changed.json()["seo_title"] is None
        assert changed.json()["updated_at"] != changed_at
        assert (await client.get("/api/v1/admin/articles")).json()["total"] == 1

        async with session_factory() as session:
            assert await session.scalar(select(func.count()).select_from(ArticleView)) == 1
            assert await session.scalar(select(func.count()).select_from(ArticleReaction)) == 0

        assert (await client.delete(f"/api/v1/admin/articles/{article_id}")).status_code == 204
        assert (await client.get(url)).status_code == 404

    async with session_factory() as session:
        assert await session.scalar(select(func.count()).select_from(ArticleContent)) == 0
        assert await session.scalar(select(func.count()).select_from(ArticleView)) == 0
