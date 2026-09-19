"""Тесты сценариев платежей без БД и без ЮKassa.

Репозиторий и шлюз подменяются простыми классами в памяти: сценарии
зависят от них только через методы, поэтому подмена прозрачна.
"""

import asyncio
from decimal import Decimal

import pytest

from app.models.payment import Payment, PaymentStatus
from app.models.user import User, UserRole
from app.services.payments.exceptions import PaymentNotFoundError
from app.services.payments.gateway import GatewayPayment, parse_payment
from app.services.payments.usecases.create_payment import CreatePaymentUseCase
from app.services.payments.usecases.sync_payment_status import SyncPaymentStatusUseCase


class FakePaymentRepository:
    """Хранит платежи в списке."""

    def __init__(self) -> None:
        self.items: list[Payment] = []

    async def get_for_user(self, payment_id: int, user_id: int) -> Payment | None:
        for payment in self.items:
            if payment.id == payment_id and payment.user_id == user_id:
                return payment
        return None

    async def get_by_provider_id(self, provider_payment_id: str) -> Payment | None:
        for payment in self.items:
            if payment.provider_payment_id == provider_payment_id:
                return payment
        return None

    async def add(self, payment: Payment) -> Payment:
        payment.id = len(self.items) + 1
        self.items.append(payment)
        return payment

    async def save(self, payment: Payment) -> Payment:
        return payment


class FakeGateway:
    """Отвечает заранее заданным статусом и запоминает, что у него просили."""

    def __init__(self, status: str = "pending") -> None:
        self.status = status
        self.created: list[dict] = []

    async def create_payment(
        self,
        amount: Decimal,
        description: str,
        customer_email: str,
        return_url: str,
        idempotence_key: str,
    ) -> GatewayPayment:
        self.created.append(
            {
                "amount": amount,
                "description": description,
                "customer_email": customer_email,
                "return_url": return_url,
                "idempotence_key": idempotence_key,
            }
        )
        return GatewayPayment(
            id="yk-1",
            status="pending",
            paid=False,
            confirmation_url="https://yookassa.ru/pay/yk-1",
        )

    async def get_payment(self, payment_id: str) -> GatewayPayment:
        return GatewayPayment(
            id=payment_id,
            status=self.status,
            paid=self.status == "succeeded",
            confirmation_url=None,
        )


def make_user() -> User:
    user = User(email="ivan@example.com", password_hash="x", full_name="Иван", phone="+79990000000", role=UserRole.CUSTOMER)
    user.id = 7
    return user


def test_create_payment_saves_gateway_data() -> None:
    repo = FakePaymentRepository()
    gateway = FakeGateway()
    usecase = CreatePaymentUseCase(repo, gateway, "https://site/oplata")

    payment = asyncio.run(usecase.execute(make_user(), Decimal("1500.00"), "Аванс 50%"))

    assert payment.id == 1
    assert payment.user_id == 7
    assert payment.status == PaymentStatus.PENDING
    assert payment.provider_payment_id == "yk-1"
    assert payment.confirmation_url == "https://yookassa.ru/pay/yk-1"
    assert gateway.created[0]["return_url"] == "https://site/oplata"
    assert gateway.created[0]["customer_email"] == "ivan@example.com"
    assert gateway.created[0]["idempotence_key"]


def test_sync_marks_succeeded_and_clears_url() -> None:
    repo = FakePaymentRepository()
    asyncio.run(
        CreatePaymentUseCase(repo, FakeGateway(), "https://site/oplata").execute(
            make_user(), Decimal("1500.00"), "Аванс 50%"
        )
    )
    usecase = SyncPaymentStatusUseCase(repo, FakeGateway(status="succeeded"))

    payment = asyncio.run(usecase.execute("yk-1"))

    assert payment.status == PaymentStatus.SUCCEEDED
    assert payment.paid_at is not None
    assert payment.confirmation_url is None


def test_sync_keeps_payment_when_status_unchanged() -> None:
    repo = FakePaymentRepository()
    asyncio.run(
        CreatePaymentUseCase(repo, FakeGateway(), "https://site/oplata").execute(
            make_user(), Decimal("1500.00"), "Аванс 50%"
        )
    )
    usecase = SyncPaymentStatusUseCase(repo, FakeGateway(status="pending"))

    payment = asyncio.run(usecase.execute("yk-1"))

    assert payment.status == PaymentStatus.PENDING
    assert payment.paid_at is None
    assert payment.confirmation_url == "https://yookassa.ru/pay/yk-1"


def test_sync_unknown_payment() -> None:
    usecase = SyncPaymentStatusUseCase(FakePaymentRepository(), FakeGateway())

    with pytest.raises(PaymentNotFoundError):
        asyncio.run(usecase.execute("nope"))


def test_parse_payment_without_confirmation() -> None:
    parsed = parse_payment({"id": "yk-2", "status": "succeeded", "paid": True})

    assert parsed.id == "yk-2"
    assert parsed.paid is True
    assert parsed.confirmation_url is None
