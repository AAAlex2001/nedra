"""Счета, банковские переводы и откаты."""

import asyncio
from decimal import Decimal
from io import BytesIO
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from pypdf import PdfReader
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.audit.models.audit import Audit
from src.audit.models.audit_company import AuditCompany
from src.audit.models.audit_document import AuditDocument
from src.audit.site.schemas.create_audit import CreateAuditRequest
from src.auth.options import AUTH_COOKIE
from src.auth.tokens import create_access_token
from src.billing.models.invoice import Invoice
from src.core.settings import Settings
from src.expertise.models.expertise import Expertise
from src.expertise.models.expertise_company import ExpertiseCompany
from src.expertise.models.expertise_document import ExpertiseDocument
from src.main import create_app
from src.notifications.models.notification import Notification
from src.notifications.repositories.notifications import NotificationRepository


@pytest.fixture(params=["audit", "expertise"])
async def invoice_work(
    request: pytest.FixtureRequest,
    session_factory: async_sessionmaker,
    audit_ids: tuple[int, int, int],
    audit_payload: CreateAuditRequest,
) -> tuple[str, int, str]:
    """Создать работу, ожидающую аванс."""

    audit_id, customer_id, expert_id = audit_ids
    async with session_factory() as session:
        if request.param == "audit":
            work = await session.get(Audit, audit_id)
            work.lead_id = expert_id
            work.status = "contract"
            work.agreed_price = Decimal("100001.01")
            session.add(AuditCompany(audit_id=audit_id, **audit_payload.company.model_dump()))
            url = f"/api/v1/audit/{audit_id}"
        else:
            work = Expertise(
                customer_id=customer_id,
                expert_id=expert_id,
                status="contract",
                price=Decimal("100001.01"),
            )
            session.add(work)
            await session.flush()
            session.add(
                ExpertiseCompany(expertise_id=work.id, **audit_payload.company.model_dump())
            )
            url = f"/api/v1/expertises/{work.id}"

        await session.commit()
        return request.param, work.id, url


async def test_invoice_stages_and_concurrent_confirmation(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    invoice_work: tuple[str, int, str],
    audit_ids: tuple[int, int, int],
    tmp_path: Path,
) -> None:
    """Выдать один счёт и подтвердить каждый этап один раз."""

    feature, work_id, url = invoice_work
    _, customer_id, expert_id = audit_ids
    settings.admin_api_token = "test-admin"
    settings.private_dir = tmp_path
    app = create_app(settings=settings)
    app.state.session_factory = session_factory

    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        client.cookies.set(AUTH_COOKIE, create_access_token(user_id=customer_id, settings=settings))
        issued = await asyncio.gather(client.post(f"{url}/invoice"), client.post(f"{url}/invoice"))
        assert [response.status_code for response in issued] == [200, 200]
        assert issued[0].json()["id"] == issued[1].json()["id"]
        invoice = issued[0].json()
        assert invoice["amount"] == "50000.51"
        invoice_id = invoice["id"]
        assert len((await client.get("/api/v1/invoices")).json()) == 1

        client.cookies.set(AUTH_COOKIE, create_access_token(user_id=expert_id, settings=settings))
        assert (await client.post(f"{url}/invoice")).status_code == 403
        client.cookies.set(AUTH_COOKIE, create_access_token(user_id=customer_id, settings=settings))

        response = await client.post(
            f"/api/v1/invoices/{invoice_id}/paid",
            files={"document": ("Поручение.pdf", b"%PDF-1.4\n%%EOF", "application/pdf")},
        )
        assert response.status_code == 200, response.text
        assert response.json()["reported_at"] is not None
        assert response.json()["paid_at"] is None
        assert (await client.get(url)).json()["status"] == "contract"
        assert (await client.post(f"/api/v1/invoices/{invoice_id}/paid")).status_code == 200
        documents = (await client.get(f"{url}/documents")).json()
        assert documents[0]["kind"] == "payment_order"

        client.headers["X-Admin-Token"] = settings.admin_api_token
        confirmed = await asyncio.gather(
            client.post(f"/api/v1/admin/invoices/{invoice_id}/pay"),
            client.post(f"/api/v1/admin/invoices/{invoice_id}/pay"),
        )
        assert sorted(response.status_code for response in confirmed) == [200, 409]
        assert (await client.get(url)).json()["status"] == (
            "plan" if feature == "audit" else "in_progress"
        )

        async with session_factory() as session:
            work = await session.get(Audit if feature == "audit" else Expertise, work_id)
            work.status = "conclusion_ready"
            await session.commit()

        final_invoice = (await client.post(f"{url}/invoice")).json()
        assert final_invoice["stage"] == "final"
        assert final_invoice["amount"] == "50000.50"
        response = await client.post(f"/api/v1/admin/invoices/{final_invoice['id']}/pay")
        assert response.status_code == 200, response.text
        assert (await client.get(url)).json()["status"] == "paid"

    async with session_factory() as session:
        assert await session.scalar(select(func.count()).select_from(Invoice)) == 2
        assert await session.scalar(select(func.count()).select_from(Notification)) == 3


async def test_failed_invoice_confirmation_rolls_back(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    invoice_work: tuple[str, int, str],
    audit_ids: tuple[int, int, int],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Откатить счёт и этап при ошибке уведомления."""

    feature, work_id, url = invoice_work
    _, customer_id, _ = audit_ids
    settings.admin_api_token = "test-admin"
    app = create_app(settings=settings)
    app.state.session_factory = session_factory

    async def fail_notification(self, *, notification) -> None:
        """Имитировать ошибку записи уведомления."""

        raise RuntimeError("notification failed")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        client.cookies.set(AUTH_COOKIE, create_access_token(user_id=customer_id, settings=settings))
        invoice_id = (await client.post(f"{url}/invoice")).json()["id"]
        monkeypatch.setattr(NotificationRepository, "add", fail_notification)
        client.headers["X-Admin-Token"] = settings.admin_api_token
        with pytest.raises(RuntimeError, match="notification failed"):
            await client.post(f"/api/v1/admin/invoices/{invoice_id}/pay")

    async with session_factory() as session:
        assert (await session.get(Invoice, invoice_id)).paid_at is None
        assert (
            await session.get(Audit if feature == "audit" else Expertise, work_id)
        ).status == "contract"


async def test_failed_invoice_report_removes_file(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    tmp_path: Path,
    invoice_work: tuple[str, int, str],
    audit_ids: tuple[int, int, int],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Удалить файл и откатить сообщение об оплате при ошибке."""

    feature, _, url = invoice_work
    _, customer_id, _ = audit_ids
    settings.private_dir = tmp_path
    app = create_app(settings=settings)
    app.state.session_factory = session_factory

    async def fail_notification(self, *, notification) -> None:
        """Имитировать ошибку записи уведомления."""

        raise RuntimeError("notification failed")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        client.cookies.set(AUTH_COOKIE, create_access_token(user_id=customer_id, settings=settings))
        invoice_id = (await client.post(f"{url}/invoice")).json()["id"]
        monkeypatch.setattr(NotificationRepository, "add", fail_notification)
        with pytest.raises(RuntimeError, match="notification failed"):
            await client.post(
                f"/api/v1/invoices/{invoice_id}/paid",
                files={"document": ("Поручение.pdf", b"%PDF-1.4\n%%EOF", "application/pdf")},
            )

    assert not [path for path in tmp_path.rglob("*") if path.is_file()]
    async with session_factory() as session:
        assert (await session.get(Invoice, invoice_id)).reported_at is None
        document_model = AuditDocument if feature == "audit" else ExpertiseDocument
        assert await session.scalar(select(func.count()).select_from(document_model)) == 0


async def test_invoice_and_act_documents(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    tmp_path: Path,
    invoice_work: tuple[str, int, str],
    audit_ids: tuple[int, int, int],
) -> None:
    """Создать читаемые PDF и закрыть акт до приёмки."""

    feature, work_id, url = invoice_work
    _, customer_id, _ = audit_ids
    settings.company_inn = "1234567890"
    settings.company_kpp = "123456789"
    settings.company_address = "Москва, тестовый адрес"
    settings.company_bank = "Тестовый банк"
    settings.company_bic = "123456789"
    settings.company_account = "1" * 20
    settings.company_corr_account = "2" * 20
    settings.company_director = "И.И. Иванов"
    app = create_app(settings=settings)
    app.state.session_factory = session_factory

    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        client.cookies.set(AUTH_COOKIE, create_access_token(user_id=customer_id, settings=settings))
        invoice_id = (await client.post(f"{url}/invoice")).json()["id"]
        invoice = await client.get(f"/api/v1/invoices/{invoice_id}/pdf")
        assert invoice.status_code == 200, invoice.text[:200] if invoice.status_code != 200 else ""
        assert invoice.headers["content-type"] == "application/pdf"
        (tmp_path / f"{feature}-invoice.pdf").write_bytes(invoice.content)
        invoice_pdf = PdfReader(BytesIO(invoice.content))
        assert len(invoice_pdf.pages) == 1
        assert "ООО Испытание" in invoice_pdf.pages[0].extract_text()
        assert "50 000,51" in invoice_pdf.pages[0].extract_text()
        assert (await client.get(f"{url}/act")).status_code == 409
        assert (await client.get("/api/v1/acts")).json() == []

        async with session_factory() as session:
            work = await session.get(Audit if feature == "audit" else Expertise, work_id)
            work.status = "accepted"
            await session.commit()

        acts = (await client.get("/api/v1/acts")).json()
        assert len(acts) == 1
        assert acts[0][f"{feature}_id"] == work_id
        act = await client.get(f"{url}/act")
        assert act.status_code == 200, act.text[:200] if act.status_code != 200 else ""
        (tmp_path / f"{feature}-act.pdf").write_bytes(act.content)
        act_pdf = PdfReader(BytesIO(act.content))
        assert len(act_pdf.pages) == 1
        assert acts[0]["number"] in act_pdf.pages[0].extract_text()
        assert "100 001,01" in act_pdf.pages[0].extract_text()

        client.cookies.clear()
        assert (await client.get(f"/api/v1/invoices/{invoice_id}/pdf")).status_code == 401
        assert (await client.get(f"{url}/act")).status_code == 401
