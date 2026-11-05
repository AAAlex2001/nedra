"""Подтверждение договора и сохранение экземпляров."""

from decimal import Decimal
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.audit.models.audit import Audit
from src.audit.models.audit_application import AuditApplication
from src.audit.models.audit_company import AuditCompany
from src.audit.site.schemas.create_audit import CreateAuditRequest
from src.auth.options import AUTH_COOKIE
from src.auth.tokens import create_access_token
from src.contracts.models.contract import Contract
from src.core.settings import Settings
from src.expertise.models.expertise import Expertise
from src.expertise.models.expertise_company import ExpertiseCompany
from src.main import create_app
from src.notifications.repositories.notifications import NotificationRepository


@pytest.fixture
def document_settings(settings: Settings, tmp_path: Path) -> Settings:
    """Реквизиты исполнителя для тестовых документов."""

    settings.private_dir = tmp_path
    settings.company_inn = "1234567890"
    settings.company_kpp = "123456789"
    settings.company_address = "Москва, тестовый адрес"
    settings.company_bank = "Тестовый банк"
    settings.company_bic = "123456789"
    settings.company_account = "1" * 20
    settings.company_corr_account = "2" * 20
    settings.company_director = "И.И. Иванов"

    return settings


@pytest.fixture(params=["audit", "expertise"])
async def contract_url(
    request: pytest.FixtureRequest,
    session_factory: async_sessionmaker,
    audit_ids: tuple[int, int, int],
    audit_payload: CreateAuditRequest,
) -> str:
    """Создать согласованную заявку с реквизитами."""

    audit_id, customer_id, expert_id = audit_ids

    async with session_factory() as session:
        if request.param == "audit":
            audit = await session.get(Audit, audit_id)
            audit.lead_id = expert_id
            audit.agreed_price = Decimal("150000")
            audit.status = "expert_ready"
            session.add_all(
                [
                    AuditApplication(
                        audit_id=audit_id,
                        object_name="Котельная",
                        details=audit_payload.details.model_dump(mode="json"),
                    ),
                    AuditCompany(audit_id=audit_id, **audit_payload.company.model_dump()),
                    Contract(audit_id=audit_id, kind="audit"),
                ]
            )
            route = f"/api/v1/audit/{audit_id}"
        else:
            expertise = Expertise(
                customer_id=customer_id,
                expert_id=expert_id,
                object_name="Документация котельной",
                object_code="tp",
                status="expert_ready",
                price=Decimal("150000"),
            )
            session.add(expertise)
            await session.flush()
            session.add_all(
                [
                    ExpertiseCompany(
                        expertise_id=expertise.id, **audit_payload.company.model_dump()
                    ),
                    Contract(expertise_id=expertise.id, kind="reequipment"),
                ]
            )
            route = f"/api/v1/expertises/{expertise.id}"

        await session.commit()

    return route


async def test_contract_is_frozen_after_confirmation(
    session_factory: async_sessionmaker,
    document_settings: Settings,
    audit_ids: tuple[int, int, int],
    contract_url: str,
) -> None:
    """Сохранить оба документа и выдавать исходные файлы."""

    _, customer_id, _ = audit_ids
    app = create_app(settings=document_settings)
    app.state.session_factory = session_factory

    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        client.cookies.set(
            AUTH_COOKIE, create_access_token(user_id=customer_id, settings=document_settings)
        )
        draft = await client.get(f"{contract_url}/signing/contract")
        assert draft.status_code == 200, draft.text

        with ZipFile(BytesIO(draft.content)) as archive:
            xml = archive.read("word/document.xml").decode()
            assert "{{" not in xml
            assert "150" in xml

        response = await client.post(f"{contract_url}/confirm")
        assert response.status_code == 200, response.text
        assert response.json()["status"] == "contract"
        contract = (await client.get(f"{contract_url}/contract")).json()
        documents = (await client.get(f"{contract_url}/documents")).json()
        assert contract["confirmed_at"] is not None
        assert {document["kind"] for document in documents} == {
            "contract",
            "nda",
        }
        signed = await client.get(f"{contract_url}/signing/contract")
        assert signed.status_code == 200
        document_settings.company_vat_rate = 20
        repeated = await client.get(f"{contract_url}/signing/contract")
        assert repeated.content == signed.content
        assert (await client.post(f"{contract_url}/confirm")).status_code == 409

    assert len(list(document_settings.private_dir.rglob("*.docx"))) == 2


async def test_failed_confirmation_removes_documents(
    session_factory: async_sessionmaker,
    document_settings: Settings,
    audit_ids: tuple[int, int, int],
    contract_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Откатить договор при ошибке сохранения уведомления."""

    async def fail_notification(self, *, notification) -> None:
        """Имитировать ошибку записи."""

        raise RuntimeError("notification failed")

    monkeypatch.setattr(NotificationRepository, "add", fail_notification)
    _, customer_id, _ = audit_ids
    app = create_app(settings=document_settings)
    app.state.session_factory = session_factory

    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        client.cookies.set(
            AUTH_COOKIE, create_access_token(user_id=customer_id, settings=document_settings)
        )

        with pytest.raises(RuntimeError, match="notification failed"):
            await client.post(f"{contract_url}/confirm")

        response = await client.get(contract_url)
        assert response.json()["status"] == "expert_ready"
        contract = (await client.get(f"{contract_url}/contract")).json()
        documents = (await client.get(f"{contract_url}/documents")).json()
        assert contract["confirmed_at"] is None
        assert documents == []

    assert not list(document_settings.private_dir.rglob("*.docx"))
