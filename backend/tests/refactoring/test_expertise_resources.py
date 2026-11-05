"""Независимое чтение разделов экспертизы."""

from datetime import UTC, datetime
from decimal import Decimal

from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from src.auth.options import AUTH_COOKIE
from src.auth.tokens import create_access_token
from src.billing.models.invoice import Invoice
from src.contracts.models.contract import Contract
from src.core.settings import Settings
from src.expertise.models.expertise import Expertise
from src.expertise.models.expertise_payment import ExpertisePayment
from src.main import create_app
from src.payments.models.payment import Payment
from src.users.enums import UserRole
from src.users.models.user import User


async def test_expertise_sections_have_independent_reads_and_access(
    *,
    session_factory: async_sessionmaker,
    database_engine: AsyncEngine,
    settings: Settings,
    audit_ids: tuple[int, int, int],
) -> None:
    """Читать разделы отдельно и закрыть их постороннему заказчику."""

    _, customer_id, expert_id = audit_ids
    paid_at = datetime.now(UTC)

    async with session_factory() as session:
        expertise = Expertise(
            customer_id=customer_id,
            expert_id=expert_id,
            object_name="Документация котельной",
            price=Decimal("1000.00"),
            status="in_progress",
        )
        payment = Payment(
            user_id=customer_id,
            amount=Decimal("500.00"),
            description="Аванс за экспертизу",
            provider_payment_id="test-provider-payment",
            status="succeeded",
            paid_at=paid_at,
        )
        stranger = User(
            email="stranger@example.com",
            password_hash="unused",
            full_name="Другой заказчик",
            phone="+79990000999",
            role=UserRole.CUSTOMER,
        )
        session.add_all([expertise, payment, stranger])
        await session.flush()
        session.add_all(
            [
                Contract(expertise_id=expertise.id, kind="reequipment"),
                ExpertisePayment(
                    expertise_id=expertise.id,
                    stage="advance",
                    payment_id=payment.id,
                    paid_at=paid_at,
                ),
                Invoice(
                    expertise_id=expertise.id,
                    stage="final",
                    amount=Decimal("500.00"),
                    payer_name="Заказчик",
                    payer_inn="7700000000",
                    payer_address="Москва",
                ),
            ]
        )
        await session.commit()
        expertise_id = expertise.id
        stranger_id = stranger.id
        payment_id = payment.id

    app = create_app(settings=settings)
    app.state.session_factory = session_factory
    url = f"/api/v1/expertises/{expertise_id}"
    queries: list[str] = []

    def remember_query(connection, cursor, statement, parameters, context, executemany) -> None:
        """Запомнить таблицы основного запроса."""

        queries.append(statement.lower())

    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        client.cookies.set(AUTH_COOKIE, create_access_token(user_id=customer_id, settings=settings))
        event.listen(database_engine.sync_engine, "before_cursor_execute", remember_query)
        try:
            response = await client.get(url)
        finally:
            event.remove(database_engine.sync_engine, "before_cursor_execute", remember_query)

        assert response.status_code == 200, response.text
        expertise = response.json()
        assert set(expertise) == {
            "id",
            "customer_id",
            "expert_id",
            "status",
            "result",
            "object",
            "conditions",
            "dates",
        }
        assert expertise["object"]["name"] == "Документация котельной"
        assert expertise["conditions"]["price"] == "1000.00"
        assert expertise["dates"]["created_at"] is not None
        for table in (
            "contracts",
            "invoices",
            "payments",
            "expertise_documents",
            "expertise_remarks",
        ):
            assert not any(f"from {table}" in query for query in queries)

        participants = (await client.get(f"{url}/participants")).json()
        assert participants["customer"]["id"] == customer_id
        assert participants["expert"]["id"] == expert_id
        assert participants["company"] is None
        assert participants["individual"] is None

        payments = (await client.get(f"{url}/payments")).json()
        assert payments["advance"]["payment"]["id"] == payment_id
        assert payments["advance"]["paid_at"] is not None
        assert payments["final"] is None
        assert payments["invoice"]["amount"] == "500.00"
        assert (await client.get(f"{url}/contract")).json()["kind"] == "reequipment"
        assert (await client.get(f"{url}/documents")).json() == []
        assert (await client.get(f"{url}/remarks")).json() == []

        client.cookies.set(AUTH_COOKIE, create_access_token(user_id=stranger_id, settings=settings))
        for suffix in ("", "/participants", "/payments", "/contract", "/documents", "/remarks"):
            response = await client.get(f"{url}{suffix}")
            assert response.status_code == 404, (suffix, response.text)

        client.cookies.clear()
        for suffix in ("", "/participants", "/payments", "/contract", "/documents", "/remarks"):
            assert (await client.get(f"{url}{suffix}")).status_code == 401
