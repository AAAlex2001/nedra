"""Подача экспертизы и выбор исполнителя."""

import asyncio
import json
from datetime import date, timedelta
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.audit.models.audit import Audit
from src.audit.site.schemas.create_audit import CreateAuditRequest
from src.auth.options import AUTH_COOKIE
from src.auth.tokens import create_access_token
from src.core.settings import Settings
from src.expertise.models.expertise import Expertise
from src.expertise.repositories.expertise_requests import ExpertiseRequestRepository
from src.main import create_app
from src.notifications.models.notification import Notification
from src.users.enums import UserRole
from src.users.models.expert_certificate import ExpertCertificate
from src.users.models.expert_profile import ExpertProfile
from src.users.models.user import User


@pytest.fixture
def expertise_payload(*, audit_payload: CreateAuditRequest) -> dict:
    """Заявка с выбором договора при принятии."""

    return {
        "object_name": "Документация котельной",
        "object_code": "kl_tp",
        "area_code": "Э1",
        "hazard_class": 2,
        "price": "100000.00",
        "customer_type": "legal",
        "company": audit_payload.company.model_dump(mode="json"),
    }


async def test_create_expertise_and_accept_once(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    audit_ids: tuple[int, int, int],
    expertise_payload: dict,
    tmp_path: Path,
) -> None:
    """Сохранить заявку и назначить только одного из двух экспертов."""

    _, customer_id, first_expert_id = audit_ids
    settings.private_dir = tmp_path
    app = create_app(settings=settings)
    app.state.session_factory = session_factory

    async with session_factory() as session:
        second_expert = User(
            email="second-expert@example.com",
            password_hash="unused",
            full_name="Второй эксперт",
            phone="+79990000003",
            role=UserRole.EXPERT,
        )
        session.add(second_expert)
        await session.flush()
        second_expert_id = second_expert.id
        session.add(ExpertProfile(user_id=second_expert_id, directions=["epb"], audit_lead=False))

        for expert_id in (first_expert_id, second_expert_id):
            session.add(
                ExpertCertificate(
                    user_id=expert_id,
                    area_code="Э1",
                    object_code="kl_tp",
                    category=1,
                    number=f"УД-{expert_id}",
                    valid_until=date.today() + timedelta(days=100),
                )
            )

        await session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        client.cookies.set(AUTH_COOKIE, create_access_token(user_id=customer_id, settings=settings))
        response = await client.post(
            "/api/v1/expertises",
            data={"payload": json.dumps(expertise_payload)},
            files={"files": ("Документация.pdf", b"%PDF-1.4\n%%EOF", "application/pdf")},
        )
        assert response.status_code == 201, response.text
        card = response.json()
        request_id = card["id"]
        assert card["status"] == "new"
        participants = (await client.get(f"/api/v1/expertises/{request_id}/participants")).json()
        contract = (await client.get(f"/api/v1/expertises/{request_id}/contract")).json()
        documents = (await client.get(f"/api/v1/expertises/{request_id}/documents")).json()
        assert participants["company"]["inn"] == expertise_payload["company"]["inn"]
        assert contract["kind"] is None
        assert len(documents) == 1
        assert card["object"]["expert_category"] == 2

        client.cookies.set(
            AUTH_COOKIE, create_access_token(user_id=first_expert_id, settings=settings)
        )
        response = await client.post(f"/api/v1/expertises/{request_id}/accept")
        assert response.status_code == 422

    async def accept_as_expert(*, expert_id: int):
        """Принять заявку в отдельном HTTP-запросе."""

        async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
            client.cookies.set(
                AUTH_COOKIE, create_access_token(user_id=expert_id, settings=settings)
            )
            return await client.post(
                f"/api/v1/expertises/{request_id}/accept",
                json={"contract_kind": "reequipment"},
            )

    responses = await asyncio.gather(
        accept_as_expert(expert_id=first_expert_id),
        accept_as_expert(expert_id=second_expert_id),
    )
    assert sorted(response.status_code for response in responses) == [200, 409]
    async with session_factory() as session:
        expertise = await session.get(Expertise, request_id)
        assert expertise.status == "expert_ready"
        assert expertise.expert_id in (first_expert_id, second_expert_id)
        assert expertise.expert_ready_at is not None
        notification_count = await session.scalar(
            select(func.count())
            .select_from(Notification)
            .where(
                Notification.user_id == customer_id,
                Notification.expertise_id == request_id,
            )
        )
        assert notification_count == 1


async def test_failed_expertise_creation_cleans_files(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    audit_ids: tuple[int, int, int],
    expertise_payload: dict,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Удалить приложения и откатить запись при ошибке репозитория."""

    original_create = ExpertiseRequestRepository.create

    async def fail_after_create(self, **arguments):
        """Имитировать ошибку после flush."""

        await original_create(self, **arguments)
        raise RuntimeError("request save failed")

    monkeypatch.setattr(ExpertiseRequestRepository, "create", fail_after_create)
    _, customer_id, _ = audit_ids
    settings.private_dir = tmp_path
    app = create_app(settings=settings)
    app.state.session_factory = session_factory
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        client.cookies.set(AUTH_COOKIE, create_access_token(user_id=customer_id, settings=settings))
        with pytest.raises(RuntimeError, match="request save failed"):
            await client.post(
                "/api/v1/expertises",
                data={"payload": json.dumps(expertise_payload)},
                files={"files": ("Документация.pdf", b"%PDF-1.4\n%%EOF", "application/pdf")},
            )

    assert not [path for path in tmp_path.rglob("*") if path.is_file()]
    async with session_factory() as session:
        assert await session.scalar(select(func.count()).select_from(Expertise)) == 0
        assert await session.scalar(select(func.count()).select_from(Audit)) == 1


async def test_accept_audit_at_customer_price(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    audit_ids: tuple[int, int, int],
) -> None:
    """Сохранить цену заказчика и дату согласия руководителя."""

    request_id, _, lead_id = audit_ids
    async with session_factory() as session:
        audit = await session.get(Audit, request_id)
        audit.customer_budget = 150000
        await session.commit()

    app = create_app(settings=settings)
    app.state.session_factory = session_factory
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        client.cookies.set(AUTH_COOKIE, create_access_token(user_id=lead_id, settings=settings))
        response = await client.post(f"/api/v1/audit/{request_id}/accept")
        assert response.status_code == 200, response.text
        assert response.json()["status"] == "expert_ready"
        assert response.json()["dates"]["lead_ready_at"] is not None

    async with session_factory() as session:
        audit = await session.get(Audit, request_id)
        assert audit.agreed_price == 150000
        assert audit.lead_ready_at is not None
