"""Команда, согласование плана и документы аудита."""

from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.audit.models.audit import Audit
from src.audit.models.audit_document import AuditDocument
from src.audit.models.audit_plan import AuditPlan
from src.audit.repositories.audit_plans import AuditPlanRepository
from src.audit.site.schemas.create_audit import CreateAuditRequest
from src.auth.options import AUTH_COOKIE
from src.auth.tokens import create_access_token
from src.core.settings import Settings
from src.main import create_app
from src.notifications.models.notification import Notification
from src.users.enums import UserRole
from src.users.models.expert_profile import ExpertProfile
from src.users.models.user import User


@pytest.fixture
def plan_payload() -> dict:
    """План без выездного этапа и совещаний."""

    return {
        "documents_start": "2026-11-10",
        "documents_end": "2026-11-12",
        "meetings": False,
        "interviewees": "Главный инженер",
    }


async def test_audit_plan_lifecycle(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    audit_ids: tuple[int, int, int],
    audit_payload: CreateAuditRequest,
    plan_payload: dict,
    tmp_path: Path,
) -> None:
    """Пройти согласование, доработку и загрузку документов через API."""

    _, customer_id, lead_id = audit_ids
    settings.private_dir = tmp_path
    app = create_app(settings=settings)
    app.state.session_factory = session_factory

    async with session_factory() as session:
        auditor = User(
            email="auditor@example.com",
            password_hash="unused",
            full_name="Участник группы",
            phone="+79990000003",
            role=UserRole.EXPERT,
        )
        session.add(auditor)
        await session.flush()
        session.add(ExpertProfile(user_id=auditor.id, audit_lead=False, directions=["sms_audit"]))
        await session.commit()
        auditor_id = auditor.id

    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        client.cookies.set(AUTH_COOKIE, create_access_token(user_id=customer_id, settings=settings))
        response = await client.post(
            "/api/v1/audit",
            data={"payload": audit_payload.model_dump_json()},
        )
        assert response.status_code == 201, response.text
        audit_id = response.json()["id"]
        audit_url = f"/api/v1/audit/{audit_id}"

        async with session_factory() as session:
            audit = await session.get(Audit, audit_id)
            audit.lead_id = lead_id
            audit.status = "plan"
            await session.commit()

        client.cookies.set(AUTH_COOKIE, create_access_token(user_id=lead_id, settings=settings))
        auditors = await client.get("/api/v1/audit/auditors")
        assert auditors.status_code == 200, auditors.text
        assert [auditor["user_id"] for auditor in auditors.json()] == [auditor_id]
        response = await client.put(f"{audit_url}/team", json={"user_ids": [customer_id]})
        assert response.status_code == 422

        for _ in range(2):
            response = await client.put(f"{audit_url}/team", json={"user_ids": [auditor_id]})
            assert response.status_code == 200, response.text

        async with session_factory() as session:
            notification_count = await session.scalar(
                select(func.count())
                .select_from(Notification)
                .where(
                    Notification.user_id == auditor_id,
                    Notification.audit_id == audit_id,
                )
            )
            assert notification_count == 1

        response = await client.post(f"{audit_url}/plan", json=plan_payload)
        assert response.status_code == 200, response.text
        card = response.json()
        assert card["status"] == "plan_review"
        plan = (await client.get(f"{audit_url}/plan")).json()
        documents = (await client.get(f"{audit_url}/documents")).json()
        assert plan["schedule"]["version"] == 1
        plan_file = next(document for document in documents if document["kind"] == "audit_plan")
        response = await client.put(f"{audit_url}/team", json={"user_ids": []})
        assert response.status_code == 409

        client.cookies.set(AUTH_COOKIE, create_access_token(user_id=customer_id, settings=settings))
        response = await client.get(f"/api/v1/audit/{audit_id}/documents/{plan_file['id']}")
        assert response.status_code == 200
        with ZipFile(BytesIO(response.content)) as document:
            xml = document.read("word/document.xml").decode()
        assert "ООО Испытание" in xml
        assert "Участник группы" in xml
        assert "Главный инженер" in xml
        assert "{{" not in xml

        response = await client.post(f"{audit_url}/plan/changes", json={"comment": "   "})
        assert response.status_code == 422
        response = await client.post(
            f"{audit_url}/plan/changes",
            json={"comment": "Перенесите документарный этап"},
        )
        assert response.status_code == 200, response.text
        assert response.json()["status"] == "plan"

        client.cookies.set(AUTH_COOKIE, create_access_token(user_id=lead_id, settings=settings))
        plan_payload["documents_start"] = "2026-11-11"
        response = await client.post(f"{audit_url}/plan", json=plan_payload)
        assert response.status_code == 200, response.text
        plan = (await client.get(f"{audit_url}/plan")).json()
        assert plan["schedule"]["version"] == 2

        client.cookies.set(AUTH_COOKIE, create_access_token(user_id=customer_id, settings=settings))
        response = await client.post(f"{audit_url}/plan/approve")
        assert response.status_code == 200, response.text
        assert response.json()["status"] == "in_progress"
        plan = (await client.get(f"{audit_url}/plan")).json()
        assert plan["approved_at"] is not None
        assert (await client.post(f"{audit_url}/plan/approve")).status_code == 409

        response = await client.post(
            f"{audit_url}/documents",
            data={"items": "1"},
            files={
                "files": (
                    "Положение.pdf",
                    b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\n%%EOF",
                    "application/pdf",
                )
            },
        )
        assert response.status_code == 200, response.text
        documents = (await client.get(f"{audit_url}/documents")).json()
        assert any(document["item_number"] == 1 for document in documents)
        response = await client.get(f"{audit_url}/documents-report")
        assert response.status_code == 200, response.text
        with ZipFile(BytesIO(response.content)) as document:
            xml = document.read("word/document.xml").decode()
        assert "Положение.pdf" in xml


async def test_failed_plan_save_removes_file_and_rolls_back(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    audit_ids: tuple[int, int, int],
    audit_payload: CreateAuditRequest,
    plan_payload: dict,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Не оставлять программу на диске после ошибки записи в БД."""

    async def fail_plan_save(self, *, plan: AuditPlan, document: AuditDocument) -> None:
        """Имитировать ошибку после записи программы."""

        self.session.add_all([plan, document])
        await self.session.flush()
        raise RuntimeError("database write failed")

    _, customer_id, lead_id = audit_ids
    settings.private_dir = tmp_path
    app = create_app(settings=settings)
    app.state.session_factory = session_factory
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        client.cookies.set(AUTH_COOKIE, create_access_token(user_id=customer_id, settings=settings))
        response = await client.post(
            "/api/v1/audit",
            data={"payload": audit_payload.model_dump_json()},
        )
        assert response.status_code == 201, response.text
        audit_id = response.json()["id"]
        async with session_factory() as session:
            audit = await session.get(Audit, audit_id)
            audit.lead_id = lead_id
            audit.status = "plan"
            await session.commit()

        monkeypatch.setattr(AuditPlanRepository, "save_with_document", fail_plan_save)
        client.cookies.set(AUTH_COOKIE, create_access_token(user_id=lead_id, settings=settings))
        with pytest.raises(RuntimeError, match="database write failed"):
            await client.post(f"/api/v1/audit/{audit_id}/plan", json=plan_payload)

    assert not [path for path in tmp_path.rglob("*") if path.is_file()]
    async with session_factory() as session:
        assert await session.get(AuditPlan, audit_id) is None
        assert (await session.get(Audit, audit_id)).status == "plan"
        assert await session.scalar(select(func.count()).select_from(AuditDocument)) == 0
