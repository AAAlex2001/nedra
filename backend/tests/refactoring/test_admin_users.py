"""Управление экспертами и доступ к сканам."""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.audit.models.audit import Audit
from src.auth.enums import ApplicationStatus
from src.auth.models.expert_application import ExpertApplication
from src.core.settings import Settings
from src.main import create_app
from src.payments.models.payment import Payment
from src.users.enums import UserRole
from src.users.models.expert_certificate import ExpertCertificate
from src.users.models.expert_profile import ExpertProfile
from src.users.models.user import User


@pytest.fixture
async def registered_expert(*, session_factory: async_sessionmaker) -> tuple[int, int, int]:
    """Создать эксперта с одобренной заявкой."""

    async with session_factory() as session:
        user = User(
            email="expert-admin@example.com",
            password_hash="unused",
            full_name="Иван Иванов",
            phone="+79990000000",
            role=UserRole.EXPERT,
        )
        session.add(user)
        await session.flush()

        application = ExpertApplication(
            email=user.email,
            password_hash=user.password_hash,
            full_name=user.full_name,
            phone=user.phone,
            directions=["industrial_safety"],
            user_id=user.id,
            status=ApplicationStatus.APPROVED,
        )
        profile = ExpertProfile(user_id=user.id, directions=application.directions)
        session.add_all([application, profile])
        await session.flush()

        certificate = ExpertCertificate(
            user_id=user.id,
            application_id=application.id,
            area_code="Э1",
            object_code="kl_tp",
            category=1,
            valid_until=date(2030, 12, 31),
            number="УД-1",
        )
        session.add(certificate)
        await session.commit()

        return user.id, application.id, certificate.id


async def test_admin_manages_expert_and_preserves_application(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    registered_expert: tuple[int, int, int],
) -> None:
    """Изменить профиль и удостоверения, затем удалить свободный аккаунт."""

    user_id, application_id, certificate_id = registered_expert
    settings.admin_api_token = "test-admin-token"
    app = create_app(settings=settings)
    app.state.session_factory = session_factory
    expert_url = f"/api/v1/admin/experts/{user_id}"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        assert (await client.get("/api/v1/admin/experts")).status_code == 401
        assert (await client.delete(expert_url)).status_code == 401
        client.headers["X-Admin-Token"] = settings.admin_api_token
        experts = (await client.get("/api/v1/admin/experts")).json()
        assert experts[0]["certificates"][0]["id"] == certificate_id
        assert "password_hash" not in experts[0]

        response = await client.patch(
            expert_url,
            json={
                "full_name": "Пётр Петров",
                "phone": "+7 (999) 123-45-67",
                "directions": ["sms_audit"],
                "audit_lead": True,
            },
        )
        assert response.status_code == 200
        assert response.json()["audit_lead"] is True
        assert response.json()["phone"] == "+79991234567"

        original_certificate_url = f"{expert_url}/certificates/{certificate_id}"
        assert (await client.delete(original_certificate_url)).status_code == 422
        certificate_payload = {
            "area_code": "Э2",
            "object_code": "kl_tp",
            "category": 2,
            "valid_until": "2030-12-31",
            "number": "УД-2",
        }
        assert (
            await client.post(f"{expert_url}/certificates", json=certificate_payload)
        ).status_code == 204
        assert (
            await client.post(f"{expert_url}/certificates", json=certificate_payload)
        ).status_code == 422
        certificate_payload["number"] = "УД-3"
        assert (
            await client.patch(original_certificate_url, json=certificate_payload)
        ).status_code == 422
        certificate_payload["area_code"] = "Э1"
        assert (
            await client.patch(original_certificate_url, json=certificate_payload)
        ).status_code == 204
        assert (await client.delete(original_certificate_url)).status_code == 204

        async with session_factory() as session:
            application = await session.get(ExpertApplication, application_id)
            assert application.full_name == "Пётр Петров"
            assert application.directions == ["sms_audit"]

        assert (await client.delete(expert_url)).status_code == 204

    async with session_factory() as session:
        assert await session.get(User, user_id) is None
        assert await session.get(ExpertProfile, user_id) is None
        application = await session.get(ExpertApplication, application_id)
        assert application.status == ApplicationStatus.REJECTED
        assert application.user_id is None
        assert application.admin_comment is not None


async def test_expert_with_payment_cannot_be_deleted(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    registered_expert: tuple[int, int, int],
) -> None:
    """Откатить удаление вместе с изменением регистрационной заявки."""

    user_id, application_id, certificate_id = registered_expert
    async with session_factory() as session:
        session.add(
            Payment(
                user_id=user_id,
                amount=Decimal("1000.00"),
                description="Исторический платёж",
                status="succeeded",
                provider_payment_id="test-payment",
            )
        )
        await session.commit()

    settings.admin_api_token = "test-admin-token"
    app = create_app(settings=settings)
    app.state.session_factory = session_factory
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        response = await client.delete(
            f"/api/v1/admin/experts/{user_id}",
            headers={"X-Admin-Token": settings.admin_api_token},
        )
        assert response.status_code == 409

    async with session_factory() as session:
        assert await session.get(User, user_id) is not None
        assert await session.get(ExpertCertificate, certificate_id) is not None
        assert (
            await session.get(ExpertApplication, application_id)
        ).status == ApplicationStatus.APPROVED


async def test_expert_assigned_to_audit_cannot_be_deleted(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    audit_ids: tuple[int, int, int],
) -> None:
    """Сохранить назначенного руководителя и историю заявки."""

    request_id, customer_id, expert_id = audit_ids
    async with session_factory() as session:
        audit = await session.get(Audit, request_id)
        audit.lead_id = expert_id
        await session.commit()

    settings.admin_api_token = "test-admin-token"
    app = create_app(settings=settings)
    app.state.session_factory = session_factory
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        headers = {"X-Admin-Token": settings.admin_api_token}
        response = await client.delete(f"/api/v1/admin/experts/{expert_id}", headers=headers)
        assert response.status_code == 409
        response = await client.get("/api/v1/admin/customers", headers=headers)
        assert response.status_code == 200
        assert response.json()[0]["user_id"] == customer_id
        assert response.json()[0]["expertises_count"] == 1

    async with session_factory() as session:
        assert (await session.get(Audit, request_id)).lead_id == expert_id


async def test_application_scan_requires_admin_and_matching_application(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    registered_expert: tuple[int, int, int],
    tmp_path: Path,
) -> None:
    """Ограничить доступ к файлу заявкой и закрытым хранилищем."""

    user_id, application_id, certificate_id = registered_expert
    settings.admin_api_token = "test-admin-token"
    settings.private_dir = tmp_path
    (tmp_path / "certificate.pdf").write_bytes(b"saved-scan")
    async with session_factory() as session:
        certificate = await session.get(ExpertCertificate, certificate_id)
        certificate.scan_path = "certificate.pdf"
        certificate.scan_name = "Удостоверение.pdf"
        await session.commit()

    app = create_app(settings=settings)
    app.state.session_factory = session_factory
    url = f"/api/v1/admin/experts/applications/{application_id}/certificates/{certificate_id}/scan"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        assert (await client.get(url)).status_code == 401
        client.headers["X-Admin-Token"] = settings.admin_api_token
        response = await client.get(url)
        assert response.status_code == 200
        assert response.content == b"saved-scan"
        assert (
            await client.get(url.replace(f"certificates/{certificate_id}", "certificates/999999"))
        ).status_code == 404

        async with session_factory() as session:
            certificate = await session.get(ExpertCertificate, certificate_id)
            certificate.scan_path = "../outside.pdf"
            await session.commit()

        assert (await client.get(url)).status_code == 404
