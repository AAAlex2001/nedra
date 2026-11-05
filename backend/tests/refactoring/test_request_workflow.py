"""Замечания, итоговый документ и приёмка."""

from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.audit.models.audit import Audit
from src.audit.models.audit_document import AuditDocument
from src.audit.models.audit_remark import AuditRemark
from src.auth.options import AUTH_COOKIE
from src.auth.tokens import create_access_token
from src.core.settings import Settings
from src.expertise.models.expertise import Expertise
from src.expertise.models.expertise_document import ExpertiseDocument
from src.expertise.models.expertise_remark import ExpertiseRemark
from src.main import create_app
from src.notifications.repositories.notifications import NotificationRepository


@pytest.mark.parametrize("service_type", ["audit", "expertise"])
async def test_remarks_conclusion_and_acceptance(
    *,
    service_type: str,
    session_factory: async_sessionmaker,
    settings: Settings,
    audit_ids: tuple[int, int, int],
    tmp_path: Path,
) -> None:
    """Пройти доработку и приёмку для обеих услуг."""

    request_id, customer_id, expert_id = audit_ids
    settings.private_dir = tmp_path

    async with session_factory() as session:
        if service_type == "audit":
            service = await session.get(Audit, request_id)
            service.lead_id = expert_id
        else:
            service = Expertise(customer_id=customer_id, expert_id=expert_id)
            session.add(service)
            await session.flush()
            request_id = service.id

        service.status = "in_progress"
        await session.commit()

    app = create_app(settings=settings)
    app.state.session_factory = session_factory
    route = "audit" if service_type == "audit" else "expertises"
    request_url = f"/api/v1/{route}/{request_id}"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        client.cookies.set(AUTH_COOKIE, create_access_token(user_id=expert_id, settings=settings))
        response = await client.post(f"{request_url}/remarks", data={"text": "  "})
        assert response.status_code == 422
        response = await client.post(f"{request_url}/remarks", data={"text": "Уточните раздел 3"})
        assert response.status_code == 200, response.text
        assert response.json()["status"] == "remarks"
        remarks = (await client.get(f"{request_url}/remarks")).json()
        assert remarks[0]["text"] == "Уточните раздел 3"
        assert (await client.post(f"{request_url}/conclusion-ready")).status_code == 409

        client.cookies.set(AUTH_COOKIE, create_access_token(user_id=customer_id, settings=settings))
        assert (await client.post(f"{request_url}/revision")).status_code == 422
        response = await client.post(
            f"{request_url}/revision",
            data={"text": "Раздел дополнен"},
            files={"files": ("Исправления.pdf", b"%PDF-1.4\n%%EOF", "application/pdf")},
        )
        assert response.status_code == 200, response.text
        card = response.json()
        assert card["status"] == "in_progress"
        remarks = (await client.get(f"{request_url}/remarks")).json()
        assert remarks[0]["resolved_at"] is not None
        assert remarks[0]["response_text"] == "Раздел дополнен"
        assert remarks[0]["documents"][0]["kind"] == "revision"

        client.cookies.set(AUTH_COOKIE, create_access_token(user_id=expert_id, settings=settings))
        response = await client.post(f"{request_url}/conclusion-ready")
        assert response.status_code == 200, response.text
        assert response.json()["status"] == "conclusion_ready"
        assert (await client.post(f"{request_url}/conclusion")).status_code == 409

        async with session_factory() as session:
            model = Audit if service_type == "audit" else Expertise
            service = await session.get(model, request_id)
            service.status = "paid"
            await session.commit()

        if service_type == "expertise":
            response = await client.post(f"{request_url}/conclusion", data={"result": "unknown"})
            assert response.status_code == 422

        response = await client.post(
            f"{request_url}/conclusion",
            data={"result": "positive"},
            files={"files": ("Заключение.pdf", b"%PDF-1.4\n%%EOF", "application/pdf")},
        )
        assert response.status_code == 200, response.text
        card = response.json()
        assert card["status"] == "sent"
        assert card["result"] == ("positive" if service_type == "expertise" else None)
        dates = card["dates"]
        assert dates["sent_at"] is not None

        client.cookies.set(AUTH_COOKIE, create_access_token(user_id=customer_id, settings=settings))
        response = await client.post(f"{request_url}/accept-work")
        assert response.status_code == 200, response.text
        assert response.json()["status"] == "accepted"
        card = response.json()
        dates = card["dates"]
        assert dates["accepted_at"] is not None
        assert (await client.post(f"{request_url}/accept-work")).status_code == 409


@pytest.mark.parametrize("feature", ["audit", "expertise"])
async def test_failed_remarks_remove_files_and_keep_status(
    *,
    feature: str,
    session_factory: async_sessionmaker,
    settings: Settings,
    audit_ids: tuple[int, int, int],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Откатить замечание и файл при ошибке уведомления."""

    audit_id, customer_id, expert_id = audit_ids
    settings.private_dir = tmp_path

    async with session_factory() as session:
        if feature == "audit":
            work = await session.get(Audit, audit_id)
            work.lead_id = expert_id
        else:
            work = Expertise(customer_id=customer_id, expert_id=expert_id)
            session.add(work)

        work.status = "in_progress"
        await session.commit()
        work_id = work.id

    async def fail_notification(self, *, notification) -> None:
        """Имитировать ошибку сохранения уведомления."""

        raise RuntimeError("notification failed")

    monkeypatch.setattr(NotificationRepository, "add", fail_notification)
    app = create_app(settings=settings)
    app.state.session_factory = session_factory
    route = "audit" if feature == "audit" else "expertises"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        client.cookies.set(AUTH_COOKIE, create_access_token(user_id=expert_id, settings=settings))

        with pytest.raises(RuntimeError, match="notification failed"):
            await client.post(
                f"/api/v1/{route}/{work_id}/remarks",
                files={"files": ("Замечания.pdf", b"%PDF-1.4\n%%EOF", "application/pdf")},
            )

    work_model = Audit if feature == "audit" else Expertise
    remark_model = AuditRemark if feature == "audit" else ExpertiseRemark
    document_model = AuditDocument if feature == "audit" else ExpertiseDocument

    async with session_factory() as session:
        work = await session.get(work_model, work_id)
        assert work.status == "in_progress"
        assert await session.scalar(select(func.count()).select_from(remark_model)) == 0
        assert await session.scalar(select(func.count()).select_from(document_model)) == 0

    assert not [path for path in tmp_path.rglob("*") if path.is_file()]
