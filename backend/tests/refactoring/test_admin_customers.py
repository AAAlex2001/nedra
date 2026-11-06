"""Удаление заказчиков администратором."""

from decimal import Decimal

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.audit.models.audit import Audit
from src.core.settings import Settings
from src.expertise.models.expertise import Expertise
from src.main import create_app
from src.payments.models.payment import Payment
from src.users.enums import UserRole
from src.users.models.user import User


@pytest.fixture
async def customer_id(*, session_factory: async_sessionmaker) -> int:
    """Создать заказчика без заявок."""

    async with session_factory() as session:
        customer = User(
            email="delete-customer@example.com",
            password_hash="unused",
            full_name="Заказчик для удаления",
            phone="+79990000000",
            role=UserRole.CUSTOMER,
        )
        session.add(customer)
        await session.commit()

        return customer.id


async def test_delete_customer_requires_admin(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    customer_id: int,
) -> None:
    """Удалить заказчика только с токеном администратора."""

    settings.admin_api_token = "test-admin-token"
    app = create_app(settings=settings)
    app.state.session_factory = session_factory
    url = f"/api/v1/admin/customers/{customer_id}"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        assert (await client.delete(url)).status_code == 401
        assert (
            await client.delete(url, headers={"X-Admin-Token": "wrong-token"})
        ).status_code == 401

        async with session_factory() as session:
            assert await session.get(User, customer_id) is not None

        client.headers["X-Admin-Token"] = settings.admin_api_token
        response = await client.delete(url)
        assert response.status_code == 204
        assert response.content == b""
        assert (await client.delete(url)).status_code == 404
        assert (await client.get("/api/v1/admin/customers")).json() == []

    async with session_factory() as session:
        assert await session.get(User, customer_id) is None


@pytest.mark.parametrize("activity", ["audit", "expertise", "payment"])
async def test_customer_with_activity_cannot_be_deleted(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    customer_id: int,
    activity: str,
) -> None:
    """Сохранить заказчика и историю его работ."""

    async with session_factory() as session:
        if activity == "audit":
            record = Audit(customer_id=customer_id, negotiation_allowed=True)
        elif activity == "expertise":
            record = Expertise(customer_id=customer_id)
        else:
            record = Payment(
                user_id=customer_id,
                amount=Decimal("1000.00"),
                description="Платёж заказчика",
                status="succeeded",
                provider_payment_id="customer-payment",
            )

        session.add(record)
        await session.commit()
        record_id = record.id

    settings.admin_api_token = "test-admin-token"
    app = create_app(settings=settings)
    app.state.session_factory = session_factory

    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        response = await client.delete(
            f"/api/v1/admin/customers/{customer_id}",
            headers={"X-Admin-Token": settings.admin_api_token},
        )
        assert response.status_code == 409
        assert "Нельзя удалить заказчика" in response.json()["detail"]

    async with session_factory() as session:
        assert await session.get(User, customer_id) is not None
        assert await session.get(type(record), record_id) is not None


async def test_customer_endpoint_cannot_delete_expert(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    customer_id: int,
) -> None:
    """Не удалять эксперта через маршрут заказчиков."""

    async with session_factory() as session:
        user = await session.get(User, customer_id)
        user.role = UserRole.EXPERT
        await session.commit()

    settings.admin_api_token = "test-admin-token"
    app = create_app(settings=settings)
    app.state.session_factory = session_factory

    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        response = await client.delete(
            f"/api/v1/admin/customers/{customer_id}",
            headers={"X-Admin-Token": settings.admin_api_token},
        )
        assert response.status_code == 404

    async with session_factory() as session:
        assert await session.get(User, customer_id) is not None
