"""Подача и рассмотрение заявок экспертов."""

import asyncio
import json
import os

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.auth.models.expert_application import ExpertApplication
from src.core.settings import Settings
from src.main import create_app
from src.users.models.expert_certificate import ExpertCertificate
from src.users.models.expert_profile import ExpertProfile
from src.users.models.user import User


@pytest.fixture
def expert_payload() -> dict:
    """Контакты и действующее удостоверение."""

    return {
        "email": "new-expert@example.com",
        "password": "Password123",
        "full_name": "Иван Иванов",
        "phone": "+79990000001",
        "directions": ["industrial_safety"],
        "certificates": [
            {
                "area_code": "Э1",
                "object_code": "kl_tp",
                "category": 1,
                "valid_until": "2028-12-31",
                "number": "УД-001",
            }
        ],
    }


async def test_approve_creates_expert_profile_and_links_certificates(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    expert_payload: dict,
) -> None:
    """Создать аккаунт только после одобрения заявки."""

    settings.admin_api_token = "test-admin-token"
    app = create_app(settings=settings)
    app.state.session_factory = session_factory
    headers = {"X-Admin-Token": settings.admin_api_token}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        response = await client.post(
            "/api/v1/experts/applications", data={"payload": json.dumps(expert_payload)}
        )
        assert response.status_code == 201
        application_id = response.json()["id"]
        async with session_factory() as session:
            assert await session.scalar(select(func.count()).select_from(User)) == 0
            assert await session.scalar(select(func.count()).select_from(ExpertCertificate)) == 1

        url = f"/api/v1/admin/experts/applications/{application_id}/approve"
        assert (await client.post(url)).status_code == 401
        approved = await client.post(url, headers=headers)
        assert approved.status_code == 200
        assert approved.json()["status"] == "approved"
        user_id = approved.json()["user_id"]
        assert (await client.post(url, headers=headers)).status_code == 409

        listed = await client.get(
            "/api/v1/admin/experts/applications?status=approved", headers=headers
        )
        assert listed.status_code == 200
        assert listed.json()[0]["certificates"][0]["number"] == "УД-001"
        login = await client.post(
            "/api/v1/auth/login",
            json={
                "email": expert_payload["email"],
                "password": expert_payload["password"],
            },
        )
        assert login.status_code == 200
        assert login.json()["role"] == "expert"

    async with session_factory() as session:
        assert await session.scalar(select(func.count()).select_from(User)) == 1
        assert (await session.get(ExpertProfile, user_id)).audit_lead is False
        assert (await session.scalar(select(ExpertCertificate))).user_id == user_id


async def test_existing_customer_is_not_promoted_by_email(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    expert_payload: dict,
) -> None:
    """Не менять роль зарегистрированного заказчика."""

    settings.admin_api_token = "test-admin-token"
    app = create_app(settings=settings)
    app.state.session_factory = session_factory
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        submitted = await client.post(
            "/api/v1/experts/applications", data={"payload": json.dumps(expert_payload)}
        )
        application_id = submitted.json()["id"]
        registered = await client.post(
            "/api/v1/auth/register",
            json={
                "email": expert_payload["email"],
                "password": expert_payload["password"],
                "full_name": expert_payload["full_name"],
                "phone": expert_payload["phone"],
            },
        )
        assert registered.status_code == 201
        response = await client.post(
            f"/api/v1/admin/experts/applications/{application_id}/approve",
            headers={"X-Admin-Token": settings.admin_api_token},
        )
        assert response.status_code == 409

    async with session_factory() as session:
        assert (await session.scalar(select(User))).role == "customer"
        assert (await session.get(ExpertApplication, application_id)).status == "pending"
        assert await session.scalar(select(func.count()).select_from(ExpertProfile)) == 0


@pytest.mark.skipif(not os.environ.get("NEDRA_TEST_DATABASE_URL"), reason="Нужна PostgreSQL")
async def test_concurrent_applications_create_one_pending_request(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    expert_payload: dict,
) -> None:
    """Не сохранять две активные заявки на одну почту."""

    app = create_app(settings=settings)
    app.state.session_factory = session_factory

    async def submit() -> int:
        """Подать заявку отдельным запросом."""

        async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
            response = await client.post(
                "/api/v1/experts/applications", data={"payload": json.dumps(expert_payload)}
            )
            return response.status_code

    assert sorted(await asyncio.gather(submit(), submit())) == [201, 409]
    async with session_factory() as session:
        assert await session.scalar(select(func.count()).select_from(ExpertApplication)) == 1
        assert await session.scalar(select(func.count()).select_from(ExpertCertificate)) == 1


@pytest.mark.skipif(not os.environ.get("NEDRA_TEST_DATABASE_URL"), reason="Нужна PostgreSQL")
async def test_approval_and_rejection_cannot_both_succeed(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    expert_payload: dict,
) -> None:
    """Сохранить одно из одновременных решений администратора."""

    settings.admin_api_token = "test-admin-token"
    app = create_app(settings=settings)
    app.state.session_factory = session_factory
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        submitted = await client.post(
            "/api/v1/experts/applications", data={"payload": json.dumps(expert_payload)}
        )
        application_id = submitted.json()["id"]

    async def review(*, action: str) -> int:
        """Рассмотреть заявку отдельным запросом."""

        async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
            response = await client.post(
                f"/api/v1/admin/experts/applications/{application_id}/{action}",
                headers={"X-Admin-Token": settings.admin_api_token},
                json={"comment": "Уточните удостоверение"},
            )
            return response.status_code

    assert sorted(await asyncio.gather(review(action="approve"), review(action="reject"))) == [
        200,
        409,
    ]
    async with session_factory() as session:
        application = await session.get(ExpertApplication, application_id)
        users_count = await session.scalar(select(func.count()).select_from(User))
        if application.status == "approved":
            assert users_count == 1
        else:
            assert application.status == "rejected"
            assert users_count == 0
