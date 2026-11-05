"""Карточки заявок и доступ участников."""

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.audit.models.audit import Audit
from src.audit.models.audit_document import AuditDocument
from src.audit.models.audit_payment import AuditPayment
from src.audit.models.audit_plan import AuditPlan
from src.audit.models.audit_remark import AuditRemark
from src.audit.schemas.audit import AuditResponse
from src.auth.options import AUTH_COOKIE
from src.auth.tokens import create_access_token
from src.core.settings import Settings
from src.expertise.models.expertise import Expertise
from src.main import create_app
from src.payments.models.payment import Payment
from src.users.enums import UserRole
from src.users.models.expert_certificate import ExpertCertificate
from src.users.models.user import User


async def test_audit_card_preserves_fields_and_hides_team_until_plan(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    audit_ids: tuple[int, int, int],
) -> None:
    """Сохранить JSON карточки и правила показа руководителя."""

    request_id, customer_id, lead_id = audit_ids
    paid_at = datetime.now(UTC)
    async with session_factory() as session:
        audit = await session.get(Audit, request_id)
        audit.lead_id = lead_id
        audit.status = "plan"
        audit.customer_budget = Decimal("120000")
        audit.agreed_price = Decimal("150000")
        payment = Payment(
            user_id=customer_id,
            amount=Decimal("75000"),
            description="Аванс",
            status="succeeded",
            provider_payment_id="card-payment",
            paid_at=paid_at,
        )
        session.add(payment)
        await session.flush()
        session.add(
            AuditPayment(
                audit_id=request_id,
                stage="advance",
                payment_id=payment.id,
                paid_at=paid_at,
            )
        )
        await session.commit()

    app = create_app(settings=settings)
    app.state.session_factory = session_factory
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        client.cookies.set(AUTH_COOKIE, create_access_token(user_id=customer_id, settings=settings))
        response = await client.get(f"/api/v1/audit/{request_id}")
        assert response.status_code == 200, response.text
        card = response.json()
        assert set(card) == set(AuditResponse.model_fields)
        assert card["conditions"]["agreed_price"] == "150000.00"
        assert card["lead_id"] == lead_id
        assert (await client.get(f"/api/v1/audit/{request_id}/team")).json() == []
        payments = (await client.get(f"/api/v1/audit/{request_id}/payments")).json()
        assert payments["advance"]["payment"]["amount"] == "75000.00"
        assert payments["advance"]["paid_at"] is not None

        client.cookies.set(AUTH_COOKIE, create_access_token(user_id=lead_id, settings=settings))
        team = (await client.get(f"/api/v1/audit/{request_id}/team")).json()
        assert team[0]["full_name"] == "Руководитель"
        assert team[0]["lead"] is True

        async with session_factory() as session:
            session.add(AuditPlan(audit_id=request_id, sent_at=datetime.now(UTC)))
            await session.commit()

        client.cookies.set(AUTH_COOKIE, create_access_token(user_id=customer_id, settings=settings))
        team = (await client.get(f"/api/v1/audit/{request_id}/team")).json()
        assert team[0]["full_name"] == "Руководитель"
        assert team[0]["user_id"] == lead_id


async def test_request_documents_are_private_and_grouped_by_remark(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    audit_ids: tuple[int, int, int],
    tmp_path: Path,
) -> None:
    """Проверить владельца заявки, привязку документа и путь файла."""

    request_id, customer_id, lead_id = audit_ids
    settings.private_dir = tmp_path
    (tmp_path / "remark.pdf").write_bytes(b"remark-file")
    async with session_factory() as session:
        stranger = User(
            email="stranger@example.com",
            password_hash="unused",
            full_name="Другой заказчик",
            phone="+79990000000",
            role=UserRole.CUSTOMER,
        )
        remark = AuditRemark(audit_id=request_id, text="Замечание")
        session.add_all([stranger, remark])
        await session.flush()
        stranger_id = stranger.id
        document = AuditDocument(
            audit_id=request_id,
            remark_id=remark.id,
            uploaded_by=lead_id,
            kind="remarks",
            file_path="remark.pdf",
            original_name="Замечания.pdf",
            size=11,
            content_type="application/pdf",
        )
        session.add(document)
        await session.commit()
        document_id = document.id

    app = create_app(settings=settings)
    app.state.session_factory = session_factory
    card_url = f"/api/v1/audit/{request_id}"
    file_url = f"{card_url}/documents/{document_id}"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        assert (await client.get(card_url)).status_code == 401
        client.cookies.set(AUTH_COOKIE, create_access_token(user_id=stranger_id, settings=settings))
        assert (await client.get(card_url)).status_code == 404
        assert (await client.get(file_url)).status_code == 404
        assert (await client.get("/api/v1/audit/my")).json() == []

        client.cookies.set(AUTH_COOKIE, create_access_token(user_id=customer_id, settings=settings))
        remarks = (await client.get(f"{card_url}/remarks")).json()
        documents = (await client.get(f"{card_url}/documents")).json()
        assert remarks[0]["documents"][0]["id"] == document_id
        assert "file_path" not in documents[0]
        assert (await client.get(file_url)).content == b"remark-file"
        assert (await client.get(f"{card_url}/documents/999999")).status_code == 404

        async with session_factory() as session:
            document = await session.get(AuditDocument, document_id)
            document.file_path = "../outside.pdf"
            await session.commit()

        assert (await client.get(file_url)).status_code == 404


async def test_incoming_expertises_require_valid_matching_certificate(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    audit_ids: tuple[int, int, int],
) -> None:
    """Исключить неподходящие и просроченные удостоверения."""

    audit_id, customer_id, expert_id = audit_ids
    async with session_factory() as session:
        expertise = Expertise(
            customer_id=customer_id,
            object_code="kl_tp",
            area_code="Э1",
            expert_category=1,
            price=Decimal("1000"),
        )
        certificate = ExpertCertificate(
            user_id=expert_id,
            area_code="Э1",
            object_code="kl_tp",
            category=1,
            valid_until=date.today() - timedelta(days=1),
            number="УД-1",
        )
        session.add_all([expertise, certificate])
        await session.commit()
        certificate_id = certificate.id
        request_id = expertise.id

    app = create_app(settings=settings)
    app.state.session_factory = session_factory
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        client.cookies.set(AUTH_COOKIE, create_access_token(user_id=expert_id, settings=settings))
        incoming = (await client.get("/api/v1/expertises/incoming")).json()
        assert incoming == []
        audit_incoming = (await client.get("/api/v1/audit/incoming")).json()
        assert [card["id"] for card in audit_incoming] == [audit_id]
        assert (await client.get(f"/api/v1/expertises/{request_id}")).status_code == 404

        async with session_factory() as session:
            certificate = await session.get(ExpertCertificate, certificate_id)
            certificate.valid_until = date.today() + timedelta(days=365)
            await session.commit()

        incoming = (await client.get("/api/v1/expertises/incoming?area_code=Э1")).json()
        assert [card["id"] for card in incoming] == [request_id]
        assert (await client.get(f"/api/v1/expertises/{request_id}")).status_code == 200


async def test_audit_price_routes_return_complete_card(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    audit_ids: tuple[int, int, int],
) -> None:
    """Провести торг через API с полной карточкой на каждом шаге."""

    request_id, customer_id, lead_id = audit_ids
    app = create_app(settings=settings)
    app.state.session_factory = session_factory
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        client.cookies.set(AUTH_COOKIE, create_access_token(user_id=lead_id, settings=settings))
        response = await client.post(f"/api/v1/audit/{request_id}/offer", json={"price": "150000"})
        assert response.status_code == 200, response.text
        assert Decimal(response.json()["conditions"]["offer_price"]) == Decimal("150000.00")
        assert set(response.json()) == set(AuditResponse.model_fields)
        assert (
            await client.post(f"/api/v1/audit/{request_id}/offer", json={"price": "150000"})
        ).status_code == 409

        client.cookies.set(AUTH_COOKIE, create_access_token(user_id=customer_id, settings=settings))
        response = await client.post(
            f"/api/v1/audit/{request_id}/offer/answer",
            json={"answer": "counter", "price": "130000"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "counter"
        assert (await client.get(f"/api/v1/audit/{request_id}/team")).json() == []

        client.cookies.set(AUTH_COOKIE, create_access_token(user_id=lead_id, settings=settings))
        response = await client.post(
            f"/api/v1/audit/{request_id}/counter/answer", json={"accept": True}
        )
        assert response.status_code == 200
        assert Decimal(response.json()["conditions"]["agreed_price"]) == Decimal("130000.00")
        assert response.json()["status"] == "expert_ready"
