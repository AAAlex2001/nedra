"""Административное управление независимыми работами."""

from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.audit.models.audit import Audit
from src.audit.models.audit_document import AuditDocument
from src.billing.models.invoice import Invoice
from src.core.settings import Settings
from src.expertise.models.expertise import Expertise
from src.expertise.models.expertise_document import ExpertiseDocument
from src.main import create_app
from src.notifications.models.notification import Notification


@pytest.mark.parametrize("feature", ["audit", "expertise"])
async def test_admin_update_and_delete_work(
    *,
    feature: str,
    session_factory: async_sessionmaker,
    settings: Settings,
    audit_ids: tuple[int, int, int],
    tmp_path: Path,
) -> None:
    """Проверить доступ, правку и удаление файлов после записи."""

    audit_id, customer_id, expert_id = audit_ids
    settings.admin_api_token = "test-admin-token"
    settings.private_dir = tmp_path
    (tmp_path / "document.pdf").write_bytes(b"test")

    async with session_factory() as session:
        if feature == "audit":
            work_id = audit_id
            document = AuditDocument(audit_id=work_id)
        else:
            expertise = Expertise(customer_id=customer_id, object_code="kl_tp")
            session.add(expertise)
            await session.flush()
            work_id = expertise.id
            document = ExpertiseDocument(expertise_id=work_id)

        document.kind = "documentation"
        document.file_path = "document.pdf"
        document.original_name = "Документ.pdf"
        document.content_type = "application/pdf"
        document.size = 4
        session.add(document)
        await session.commit()

    app = create_app(settings=settings)
    app.state.session_factory = session_factory
    collection = "audits" if feature == "audit" else "expertises"
    url = f"/api/v1/admin/{collection}"
    payload = {"status": "expert_ready", "price": "150000.00"}
    payload["lead_id" if feature == "audit" else "expert_id"] = expert_id
    if feature == "expertise":
        payload["contract_kind"] = "reequipment"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        assert (await client.get(url)).status_code == 401
        sections = (
            ["", "/contract", "/customer", "/application"]
            if feature == "audit"
            else [
                "",
                "/contract",
                "/participants",
            ]
        )
        for section in sections:
            assert (await client.get(f"{url}/{work_id}{section}")).status_code == 401
        assert (await client.patch(f"{url}/{work_id}", json=payload)).status_code == 401
        assert (await client.delete(f"{url}/{work_id}")).status_code == 401
        client.headers["X-Admin-Token"] = settings.admin_api_token
        response = await client.patch(f"{url}/{work_id}", json=payload)
        assert response.status_code == 204, response.text
        records = (await client.get(url)).json()
        assert records[0]["status"] == "expert_ready"
        assert records[0]["customer_name"] == "Заказчик"
        assert records[0]["price"] == "150000.00"
        for section in sections:
            assert (await client.get(f"{url}/{work_id}{section}")).status_code == 200
            assert (await client.get(f"{url}/999999{section}")).status_code == 404
        assert (await client.delete(f"{url}/{work_id}")).status_code == 204
        assert (await client.get(url)).json() == []

    assert not (tmp_path / "document.pdf").exists()


@pytest.mark.parametrize("feature", ["audit", "expertise"])
async def test_admin_cannot_delete_invoice_history(
    *,
    feature: str,
    session_factory: async_sessionmaker,
    settings: Settings,
    audit_ids: tuple[int, int, int],
) -> None:
    """Сохранить работу и счёт при запрещённом удалении."""

    audit_id, customer_id, _ = audit_ids
    settings.admin_api_token = "test-admin-token"
    async with session_factory() as session:
        invoice = Invoice(
            stage="advance",
            amount=1000,
            payer_name="Компания",
            payer_inn="7700000000",
            payer_address="Москва",
        )
        if feature == "audit":
            work_id = audit_id
            invoice.audit_id = work_id
        else:
            expertise = Expertise(customer_id=customer_id)
            session.add(expertise)
            await session.flush()
            work_id = expertise.id
            invoice.expertise_id = work_id
        session.add(invoice)
        await session.commit()

    app = create_app(settings=settings)
    app.state.session_factory = session_factory
    collection = "audits" if feature == "audit" else "expertises"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        client.headers["X-Admin-Token"] = settings.admin_api_token
        response = await client.delete(f"/api/v1/admin/{collection}/{work_id}")
        assert response.status_code == 409, response.text

    async with session_factory() as session:
        assert await session.scalar(select(func.count()).select_from(Invoice)) == 1
        assert await session.get(Audit if feature == "audit" else Expertise, work_id) is not None


async def test_admin_releases_consultation_once(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    audit_ids: tuple[int, int, int],
) -> None:
    """Уведомить руководителей при завершении консультации."""

    audit_id, _, _ = audit_ids
    settings.admin_api_token = "test-admin-token"
    async with session_factory() as session:
        audit = await session.get(Audit, audit_id)
        audit.status = "consultation"
        await session.commit()

    app = create_app(settings=settings)
    app.state.session_factory = session_factory
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        client.headers["X-Admin-Token"] = settings.admin_api_token
        for _ in range(2):
            response = await client.patch(
                f"/api/v1/admin/audits/{audit_id}",
                json={"status": "new", "price": "150000", "lead_id": None},
            )
            assert response.status_code == 204, response.text

    async with session_factory() as session:
        assert await session.scalar(select(func.count()).select_from(Notification)) == 1
