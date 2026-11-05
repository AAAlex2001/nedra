"""Платёжный провайдер и повторные уведомления."""

import asyncio
import json
from decimal import Decimal

import httpx
import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.auth.options import AUTH_COOKIE
from src.auth.tokens import create_access_token
from src.core.settings import Settings
from src.expertise.models.expertise import Expertise
from src.main import create_app
from src.notifications.models.notification import Notification
from src.notifications.repositories.notifications import NotificationRepository
from src.payments.dependencies import get_payment_gateway
from src.payments.gateway import YooKassaGateway
from src.payments.models.payment import Payment
from src.payments.options import YOOKASSA_API_URL


@pytest.fixture
async def online_expertise(
    session_factory: async_sessionmaker,
    audit_ids: tuple[int, int, int],
) -> int:
    """Экспертиза физического лица перед оплатой."""

    _, customer_id, expert_id = audit_ids
    async with session_factory() as session:
        expertise = Expertise(
            customer_id=customer_id,
            expert_id=expert_id,
            customer_type="individual",
            status="contract",
            price=Decimal("100001.01"),
        )
        session.add(expertise)
        await session.commit()
        return expertise.id


@pytest.mark.parametrize("instant_payment", [False, True])
async def test_online_payment_is_applied_once(
    session_factory: async_sessionmaker,
    settings: Settings,
    audit_ids: tuple[int, int, int],
    online_expertise: int,
    instant_payment: bool,
) -> None:
    """Повторные запросы не дублируют оплату и уведомление."""

    _, customer_id, expert_id = audit_ids
    provider_paid = instant_payment
    creation_requests = []

    def provider(request: httpx.Request) -> httpx.Response:
        assert request.url.path.startswith("/v3/payments")
        if request.method == "POST":
            creation_requests.append(json.loads(request.content))
            assert request.headers["Idempotence-Key"]
        return httpx.Response(
            200,
            json={
                "id": "provider-payment",
                "status": "succeeded" if provider_paid else "pending",
                "paid": provider_paid,
                "amount": {"value": "50000.51", "currency": "RUB"},
                "confirmation": {"confirmation_url": "https://payments.example/checkout"},
            },
        )

    settings.payment_return_url = "https://test/kabinet"
    app = create_app(settings=settings)
    app.state.session_factory = session_factory
    async with httpx.AsyncClient(
        base_url=YOOKASSA_API_URL,
        transport=httpx.MockTransport(provider),
    ) as provider_client:
        app.dependency_overrides[get_payment_gateway] = lambda: YooKassaGateway(
            client=provider_client,
            vat_code=1,
        )
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="https://test",
        ) as client:
            client.cookies.set(
                AUTH_COOKIE, create_access_token(user_id=customer_id, settings=settings)
            )
            url = f"/api/v1/expertises/{online_expertise}"
            created = await client.post(f"{url}/payment")
            assert created.status_code == 200, created.text
            payment_id = created.json()["id"]
            if not instant_payment:
                repeated = await asyncio.gather(
                    client.post(f"{url}/payment"),
                    client.post(f"{url}/payment"),
                )
                assert all(response.json()["id"] == payment_id for response in repeated)
            assert len(creation_requests) == 1
            assert creation_requests[0]["amount"]["value"] == "50000.51"

            client.cookies.set(
                AUTH_COOKIE, create_access_token(user_id=expert_id, settings=settings)
            )
            assert (await client.post(f"/api/v1/payments/{payment_id}/refresh")).status_code == 404
            client.cookies.set(
                AUTH_COOKIE, create_access_token(user_id=customer_id, settings=settings)
            )
            provider_paid = True
            webhook = {
                "type": "notification",
                "event": "payment.succeeded",
                "object": {"id": "provider-payment"},
            }
            confirmed = await asyncio.gather(
                client.post("/api/v1/payments/yookassa/webhook", json=webhook),
                client.post(f"/api/v1/payments/{payment_id}/refresh"),
                client.post("/api/v1/payments/yookassa/webhook", json=webhook),
            )
            assert [response.status_code for response in confirmed] == [200, 200, 200]
            assert (await client.get(url)).json()["status"] == "in_progress"
            payment = (await client.get(f"/api/v1/payments/{payment_id}")).json()
            assert payment["paid_at"] is not None
            assert payment["confirmation_url"] is None

    async with session_factory() as session:
        assert await session.scalar(select(func.count()).select_from(Payment)) == 1
        assert await session.scalar(select(func.count()).select_from(Notification)) == 1


@pytest.mark.parametrize("invalid_field", ["amount", "currency", "id", "paid", "notification"])
async def test_invalid_confirmation_rolls_back(
    session_factory: async_sessionmaker,
    settings: Settings,
    audit_ids: tuple[int, int, int],
    online_expertise: int,
    invalid_field: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Некорректный ответ или ошибка записи не подтверждают оплату."""

    _, customer_id, _ = audit_ids
    from src.expertise.models.expertise_payment import ExpertisePayment

    async with session_factory() as session:
        payment = Payment(
            user_id=customer_id,
            amount=Decimal("50000.51"),
            currency="RUB",
            description="Аванс",
            status="pending",
            provider_payment_id="provider-payment",
        )
        session.add(payment)
        await session.flush()
        session.add(
            ExpertisePayment(expertise_id=online_expertise, stage="advance", payment_id=payment.id)
        )
        await session.commit()
        payment_id = payment.id

    response_data = {
        "id": "wrong" if invalid_field == "id" else "provider-payment",
        "status": "succeeded",
        "paid": invalid_field != "paid",
        "amount": {
            "value": "1.00" if invalid_field == "amount" else "50000.51",
            "currency": "USD" if invalid_field == "currency" else "RUB",
        },
    }

    async def fail_notification(self, *, notification):
        raise RuntimeError("notification unavailable")

    if invalid_field == "notification":
        monkeypatch.setattr(NotificationRepository, "add", fail_notification)

    app = create_app(settings=settings)
    app.state.session_factory = session_factory
    async with httpx.AsyncClient(
        base_url=YOOKASSA_API_URL,
        transport=httpx.MockTransport(lambda request: httpx.Response(200, json=response_data)),
    ) as provider_client:
        app.dependency_overrides[get_payment_gateway] = lambda: YooKassaGateway(
            client=provider_client, vat_code=1
        )
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app, raise_app_exceptions=False),
            base_url="https://test",
        ) as client:
            client.cookies.set(
                AUTH_COOKIE, create_access_token(user_id=customer_id, settings=settings)
            )
            response = await client.post(f"/api/v1/payments/{payment_id}/refresh")
            assert response.status_code == (500 if invalid_field == "notification" else 502)

    async with session_factory() as session:
        assert (await session.get(Payment, payment_id)).status == "pending"
        assert (await session.get(Expertise, online_expertise)).status == "contract"
        assert await session.scalar(select(func.count()).select_from(Notification)) == 0


async def test_payment_creation_retry_uses_same_key(
    session_factory: async_sessionmaker,
    settings: Settings,
    audit_ids: tuple[int, int, int],
    online_expertise: int,
) -> None:
    """Повторить запрос после таймаута с прежним ключом."""

    _, customer_id, _ = audit_ids
    request_keys = []

    def provider(request: httpx.Request) -> httpx.Response:
        request_keys.append(request.headers["Idempotence-Key"])

        if len(request_keys) == 1:
            raise httpx.ReadTimeout("response lost", request=request)

        return httpx.Response(
            200,
            json={
                "id": "one-provider-payment",
                "status": "pending",
                "paid": False,
                "amount": {"value": "50000.51", "currency": "RUB"},
                "confirmation": {"confirmation_url": "https://payments.example/checkout"},
            },
        )

    settings.payment_return_url = "https://test/kabinet"
    app = create_app(settings=settings)
    app.state.session_factory = session_factory

    async with httpx.AsyncClient(
        base_url=YOOKASSA_API_URL,
        transport=httpx.MockTransport(provider),
    ) as provider_client:
        app.dependency_overrides[get_payment_gateway] = lambda: YooKassaGateway(
            client=provider_client,
            vat_code=1,
        )
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="https://test",
        ) as client:
            client.cookies.set(
                AUTH_COOKIE, create_access_token(user_id=customer_id, settings=settings)
            )
            url = f"/api/v1/expertises/{online_expertise}/payment"
            assert (await client.post(url)).status_code == 502
            assert (await client.post(url)).status_code == 200

    assert len(request_keys) == 2
    assert request_keys[0] == request_keys[1]

    async with session_factory() as session:
        assert await session.scalar(select(func.count()).select_from(Payment)) == 1
