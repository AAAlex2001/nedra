"""Профиль эксперта и удостоверения."""

import asyncio
import os
from datetime import date
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.auth.options import AUTH_COOKIE
from src.auth.tokens import create_access_token
from src.core.settings import Settings
from src.main import create_app
from src.users.models.expert_certificate import ExpertCertificate
from src.users.models.expert_profile import ExpertProfile


@pytest.fixture
async def certificate_ids(
    *,
    session_factory: async_sessionmaker,
    audit_ids: tuple[int, int, int],
) -> tuple[int, int]:
    """Два удостоверения одного эксперта."""

    _, _, expert_id = audit_ids
    async with session_factory() as session:
        first = ExpertCertificate(
            user_id=expert_id,
            area_code="Э1",
            object_code="kl_tp",
            category=1,
            valid_until=date(2028, 12, 31),
            number="Первое",
        )
        second = ExpertCertificate(
            user_id=expert_id,
            area_code="Э2",
            object_code="d",
            category=2,
            valid_until=date(2028, 12, 31),
            number="Второе",
        )
        session.add_all([first, second])
        await session.commit()
        return first.id, second.id


async def test_expert_profile_and_certificate_changes(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    audit_ids: tuple[int, int, int],
    certificate_ids: tuple[int, int],
) -> None:
    """Изменить направления и удостоверение через кабинет."""

    _, _, expert_id = audit_ids
    first_id, second_id = certificate_ids
    app = create_app(settings=settings)
    app.state.session_factory = session_factory
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        catalog = await client.get("/api/v1/experts/catalog")
        assert catalog.status_code == 200
        assert catalog.json()["areas"][0]["code"] == "Э1"
        assert isinstance(catalog.json()["areas"][0]["objects"], list)
        client.cookies.set(AUTH_COOKIE, create_access_token(user_id=expert_id, settings=settings))
        profile = await client.get("/api/v1/experts/me")
        assert profile.status_code == 200
        assert len(profile.json()["certificates"]) == 2
        updated = await client.put(
            "/api/v1/experts/me/directions", json={"directions": ["industrial_safety"]}
        )
        assert updated.status_code == 200
        assert updated.json()["directions"] == ["industrial_safety"]
        assert (await client.get("/api/v1/audit/incoming")).json() == []
        restored = await client.put(
            "/api/v1/experts/me/directions",
            json={"directions": ["industrial_safety", "sms_audit"]},
        )
        assert restored.status_code == 200
        async with session_factory() as session:
            profile = await session.get(ExpertProfile, expert_id)
            assert profile.audit_lead is False

        certificate = {
            "area_code": "Э1",
            "object_code": "kl_tp",
            "category": 2,
            "valid_until": "2029-12-31",
            "number": "Изменённое",
        }
        updated = await client.patch(
            f"/api/v1/experts/me/certificates/{first_id}", json=certificate
        )
        assert updated.status_code == 200
        assert updated.json()["certificates"][0]["number"] == "Изменённое"
        assert (
            await client.post("/api/v1/experts/me/certificates", json=certificate)
        ).status_code == 422
        assert (
            await client.delete(f"/api/v1/experts/me/certificates/{second_id}")
        ).status_code == 200
        assert (
            await client.delete(f"/api/v1/experts/me/certificates/{first_id}")
        ).status_code == 422


@pytest.mark.skipif(not os.environ.get("NEDRA_TEST_DATABASE_URL"), reason="Нужна PostgreSQL")
async def test_concurrent_deletions_keep_one_certificate(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    audit_ids: tuple[int, int, int],
    certificate_ids: tuple[int, int],
) -> None:
    """Не удалить последнее удостоверение при одновременных запросах."""

    _, _, expert_id = audit_ids
    app = create_app(settings=settings)
    app.state.session_factory = session_factory

    async def delete(*, certificate_id: int) -> int:
        """Удалить удостоверение отдельным запросом."""

        async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
            client.cookies.set(
                AUTH_COOKIE, create_access_token(user_id=expert_id, settings=settings)
            )
            response = await client.delete(f"/api/v1/experts/me/certificates/{certificate_id}")
            return response.status_code

    statuses = await asyncio.gather(
        delete(certificate_id=certificate_ids[0]), delete(certificate_id=certificate_ids[1])
    )
    assert sorted(statuses) == [200, 422]
    async with session_factory() as session:
        assert await session.scalar(select(func.count()).select_from(ExpertCertificate)) == 1


async def test_certificate_scan_requires_owner_and_stays_inside_storage(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    audit_ids: tuple[int, int, int],
    certificate_ids: tuple[int, int],
    tmp_path: Path,
) -> None:
    """Открыть свой скан и отклонить путь за пределами хранилища."""

    _, customer_id, expert_id = audit_ids
    first_id, _ = certificate_ids
    settings.private_dir = tmp_path / "private"
    scan = settings.private_dir / "scans" / "certificate.pdf"
    scan.parent.mkdir(parents=True)
    scan.write_bytes(b"%PDF-1.4 test")
    async with session_factory() as session:
        certificate = await session.get(ExpertCertificate, first_id)
        certificate.scan_path = "scans/certificate.pdf"
        await session.commit()

    app = create_app(settings=settings)
    app.state.session_factory = session_factory
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        client.cookies.set(AUTH_COOKIE, create_access_token(user_id=customer_id, settings=settings))
        assert (
            await client.get(f"/api/v1/experts/me/certificates/{first_id}/scan")
        ).status_code == 403
        client.cookies.set(AUTH_COOKIE, create_access_token(user_id=expert_id, settings=settings))
        response = await client.get(f"/api/v1/experts/me/certificates/{first_id}/scan")
        assert response.status_code == 200
        assert response.content == scan.read_bytes()
        async with session_factory() as session:
            certificate = await session.get(ExpertCertificate, first_id)
            certificate.scan_path = "../outside.pdf"
            await session.commit()
        assert (
            await client.get(f"/api/v1/experts/me/certificates/{first_id}/scan")
        ).status_code == 404
