"""Доступ к уведомлениям и отметки о прочтении."""

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.auth.options import AUTH_COOKIE
from src.auth.tokens import create_access_token
from src.core.settings import Settings
from src.main import create_app
from src.notifications.models.notification import Notification


async def test_notifications_are_private_and_read_time_is_preserved(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    audit_ids: tuple[int, int, int],
) -> None:
    """Скрыть чужие уведомления и сохранить дату первого прочтения."""

    request_id, customer_id, expert_id = audit_ids
    async with session_factory() as session:
        own = Notification(user_id=customer_id, audit_id=request_id, text="Ваше уведомление")
        other = Notification(user_id=expert_id, audit_id=request_id, text="Чужое уведомление")
        session.add_all([own, other])
        await session.commit()
        own_id, other_id = own.id, other.id

    app = create_app(settings=settings)
    app.state.session_factory = session_factory
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        client.cookies.set(AUTH_COOKIE, create_access_token(user_id=customer_id, settings=settings))
        notifications = await client.get("/api/v1/notifications")
        assert notifications.status_code == 200
        assert len(notifications.json()) == 1
        assert notifications.json()[0]["audit_id"] == request_id
        assert notifications.json()[0]["expertise_id"] is None
        assert (await client.post(f"/api/v1/notifications/{other_id}/read")).status_code == 404

        first_read = await client.post(f"/api/v1/notifications/{own_id}/read")
        second_read = await client.post(f"/api/v1/notifications/{own_id}/read")
        assert first_read.status_code == second_read.status_code == 200
        assert first_read.json()["read_at"] == second_read.json()["read_at"]
        assert first_read.json()["read_at"] is not None
        assert (await client.post("/api/v1/notifications/read-all")).status_code == 200

    async with session_factory() as session:
        assert (await session.get(Notification, other_id)).read_at is None


async def test_read_all_marks_all_owned_notifications(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    audit_ids: tuple[int, int, int],
) -> None:
    """Прочитать свои уведомления, включая записи за пределами страницы."""

    request_id, customer_id, expert_id = audit_ids
    async with session_factory() as session:
        session.add_all(
            [
                Notification(user_id=customer_id, audit_id=request_id, text=f"Уведомление {number}")
                for number in range(60)
            ]
        )
        other = Notification(user_id=expert_id, text="Для другого пользователя")
        session.add(other)
        await session.commit()
        other_id = other.id

    app = create_app(settings=settings)
    app.state.session_factory = session_factory
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        client.cookies.set(AUTH_COOKIE, create_access_token(user_id=customer_id, settings=settings))
        response = await client.post("/api/v1/notifications/read-all")
        assert response.status_code == 200
        assert len(response.json()) == 50
        response = await client.get("/api/v1/notifications?limit=100")
        assert len(response.json()) == 60
        assert all(item["read_at"] is not None for item in response.json())

    async with session_factory() as session:
        assert (await session.get(Notification, other_id)).read_at is None
