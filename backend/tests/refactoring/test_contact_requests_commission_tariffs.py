"""Обращения, комиссия и административные тарифы."""

import asyncio
from decimal import Decimal

from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.commission.models.commission_application import CommissionApplication
from src.core.settings import Settings
from src.main import create_app
from src.requests.models.contact_request import ContactRequest
from src.tariffs.admin.schemas.save_tariffs import SaveTariffsRequest
from src.tariffs.admin.usecases.save_tariffs import SaveTariffsUseCase
from src.tariffs.models.tariff import Tariff
from src.tariffs.repositories.tariffs import TariffRepository
from src.users.models.user import User


async def test_contact_request_creation_and_admin_access(
    *, session_factory: async_sessionmaker, settings: Settings
) -> None:
    """Сохранить обращение и закрыть управление от посетителей."""

    settings.admin_api_token = "test-admin-token"
    app = create_app(settings=settings)
    app.state.session_factory = session_factory
    payload = {
        "name": "Иван Петров",
        "telephone": "+79990000000",
        "email": "ivan@example.com",
        "activity": 0,
        "company_name": "Компания",
        "inn": "1234567890",
        "comment": "Нужна консультация",
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        response = await client.post("/api/v1/request", json=payload)
        assert response.status_code == 201
        request_id = response.json()["request_id"]
        assert response.json()["direction"] == 0
        assert response.json()["comment"] == payload["comment"]
        assert (await client.get("/api/v1/requests")).status_code == 401
        assert (await client.delete(f"/api/v1/request/{request_id}")).status_code == 401

        payload["activity"] = 999
        assert (await client.post("/api/v1/request", json=payload)).status_code == 422
        client.headers["X-Admin-Token"] = settings.admin_api_token
        response = await client.get("/api/v1/requests")
        assert response.status_code == 200
        assert [request["request_id"] for request in response.json()] == [request_id]
        assert (await client.delete(f"/api/v1/request/{request_id}")).status_code == 204
        assert (await client.delete(f"/api/v1/request/{request_id}")).status_code == 404

    async with session_factory() as session:
        assert await session.scalar(select(func.count()).select_from(ContactRequest)) == 0


async def test_commission_validates_attestations_without_creating_account(
    *, session_factory: async_sessionmaker, settings: Settings
) -> None:
    """Проверить аттестации и сохранить только заявку кандидата."""

    settings.admin_api_token = "test-admin-token"
    app = create_app(settings=settings)
    app.state.session_factory = session_factory
    payload = {
        "full_name": " Иван Петров ",
        "phone": "+79990000000",
        "email": "ivan@example.com",
        "attestations": [{"area_code": "Э1", "object_code": "kl_tp", "category": 1}],
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        response = await client.post("/api/v1/commission/applications", json=payload)
        assert response.status_code == 201, response.text
        application_id = response.json()["id"]
        assert response.json()["full_name"] == "Иван Петров"
        assert response.json()["attestations"] == payload["attestations"]
        payload["attestations"][0]["object_code"] = "unknown"
        assert (
            await client.post("/api/v1/commission/applications", json=payload)
        ).status_code == 422
        payload["full_name"] = "   "
        assert (
            await client.post("/api/v1/commission/applications", json=payload)
        ).status_code == 422
        assert (await client.get("/api/v1/admin/commission/applications")).status_code == 401

        client.headers["X-Admin-Token"] = settings.admin_api_token
        response = await client.get("/api/v1/admin/commission/applications")
        assert len(response.json()) == 1
        delete_url = f"/api/v1/admin/commission/applications/{application_id}"
        assert (await client.delete(delete_url)).status_code == 204
        assert (await client.delete(delete_url)).status_code == 404

    async with session_factory() as session:
        assert await session.scalar(select(func.count()).select_from(User)) == 0
        assert await session.scalar(select(func.count()).select_from(CommissionApplication)) == 0


async def test_tariff_batch_validation_and_removal(
    *, session_factory: async_sessionmaker, settings: Settings
) -> None:
    """Отклонить весь неверный пакет и удалить тариф пустой ценой."""

    settings.admin_api_token = "test-admin-token"
    app = create_app(settings=settings)
    app.state.session_factory = session_factory
    payload = {"items": [{"area_code": "audit", "object_code": "supb", "price": "150000.00"}]}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        assert (await client.get("/api/v1/tariffs")).json() == []
        assert (await client.put("/api/v1/admin/tariffs", json=payload)).status_code == 401
        client.headers["X-Admin-Token"] = settings.admin_api_token
        response = await client.put("/api/v1/admin/tariffs", json=payload)
        assert response.status_code == 200
        assert response.json()[0]["price"] == "150000.00"

        payload["items"][0]["price"] = "200000.00"
        payload["items"].append({"area_code": "unknown", "object_code": "kl", "price": "100.00"})
        assert (await client.put("/api/v1/admin/tariffs", json=payload)).status_code == 422
        assert (await client.get("/api/v1/tariffs")).json()[0]["price"] == "150000.00"
        payload["items"] = [{"area_code": "audit", "object_code": "supb", "price": "99999.99"}]
        assert (await client.put("/api/v1/admin/tariffs", json=payload)).status_code == 422
        payload["items"][0]["price"] = None
        assert (await client.put("/api/v1/admin/tariffs", json=payload)).json() == []


async def test_concurrent_tariff_creation_keeps_one_price(
    *, session_factory: async_sessionmaker
) -> None:
    """Одновременно создать одну пару без дубликатов и ошибок уникальности."""

    async def save_price(*, price: str) -> None:
        """Сохранить тариф отдельной транзакцией."""

        async with session_factory() as session:
            usecase = SaveTariffsUseCase(session=session, tariffs=TariffRepository(session=session))
            payload = SaveTariffsRequest(
                items=[{"area_code": "audit", "object_code": "supb", "price": price}]
            )
            await usecase.execute(payload=payload)

    await asyncio.gather(save_price(price="150000.00"), save_price(price="200000.00"))
    async with session_factory() as session:
        tariffs = list(await session.scalars(select(Tariff)))
        assert len(tariffs) == 1
        assert tariffs[0].price in (Decimal("150000.00"), Decimal("200000.00"))
