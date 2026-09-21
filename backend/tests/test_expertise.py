"""Тесты экспертизы без БД и без диска: подача, путь по шагам, платежи."""

import asyncio
from datetime import date
from decimal import Decimal

import pytest

from app.models.expert import ExpertCertificate
from app.models.expertise import Expertise, ExpertiseResult, ExpertiseStatus
from app.models.notification import Notification
from app.models.payment import Payment, PaymentStatus
from app.models.tariff import Tariff
from app.models.user import User, UserRole
from app.schemas.expertise import ExpertiseInSchema
from app.services.expertise.access import can_view
from app.services.expertise.exceptions import (
    ExpertiseAccessError,
    ExpertiseStateError,
    InvalidExpertiseError,
    PriceMissingError,
)
from app.services.expertise.money import split_price
from app.services.expertise.repo import certificate_fits
from app.services.expertise.usecases.accept_expertise import AcceptExpertiseUseCase
from app.services.expertise.usecases.accept_work import AcceptWorkUseCase
from app.services.expertise.usecases.apply_expertise_payment import ApplyExpertisePaymentUseCase
from app.services.expertise.usecases.confirm_expertise import ConfirmExpertiseUseCase
from app.services.expertise.usecases.create_expertise import CreateExpertiseUseCase
from app.services.expertise.usecases.create_expertise_payment import CreateExpertisePaymentUseCase
from app.services.expertise.usecases.mark_conclusion_ready import MarkConclusionReadyUseCase
from app.services.expertise.usecases.resubmit_documentation import ResubmitDocumentationUseCase
from app.services.expertise.usecases.send_conclusion import SendConclusionUseCase
from app.services.expertise.usecases.send_remarks import SendRemarksUseCase
from app.services.expertise.validators import resolve_category, validate_pair
from app.services.files.storage import StoredFile


class FakeExpertiseRepository:
    def __init__(self) -> None:
        self.items: list[Expertise] = []

    async def add(self, expertise: Expertise) -> Expertise:
        expertise.id = len(self.items) + 1
        self.items.append(expertise)
        return expertise

    async def save(self, expertise: Expertise) -> Expertise:
        return expertise

    async def get_by_payment_id(self, payment_id: int) -> Expertise | None:
        for item in self.items:
            if payment_id in (item.advance_payment_id, item.final_payment_id):
                return item
        return None


class FakeProfileRepository:
    def __init__(self, experts: list[User], certificates: list[ExpertCertificate] | None = None) -> None:
        self.experts = experts
        self.certificates = certificates or []

    async def list_certified(self, object_code: str, area_code: str, max_category: int) -> list[User]:
        return self.experts

    async def list_certificates(self, user_id: int) -> list[ExpertCertificate]:
        return self.certificates


class FakeNotificationRepository:
    def __init__(self) -> None:
        self.added: list[Notification] = []

    def add_all(self, notifications: list[Notification]) -> None:
        self.added.extend(notifications)


class FakeTariffRepository:
    def __init__(self, price: Decimal | None) -> None:
        self.price = price

    async def get(self, area_code: str, object_code: str) -> Tariff | None:
        if self.price is None:
            return None
        return Tariff(area_code=area_code, object_code=object_code, price=self.price)


class FakePaymentRepository:
    def __init__(self) -> None:
        self.items: list[Payment] = []

    async def get_by_id(self, payment_id: int) -> Payment | None:
        for item in self.items:
            if item.id == payment_id:
                return item
        return None


class FakeCreatePayment:
    def __init__(self, payments: FakePaymentRepository) -> None:
        self.payments = payments
        self.calls: list[tuple[Decimal, str]] = []

    async def execute(self, user: User, amount: Decimal, description: str) -> Payment:
        self.calls.append((amount, description))
        payment = Payment(
            user_id=user.id,
            amount=amount,
            description=description,
            status=PaymentStatus.PENDING,
            provider_payment_id=f"yk-{len(self.payments.items) + 1}",
            confirmation_url="https://yookassa.ru/pay",
        )
        payment.id = len(self.payments.items) + 1
        self.payments.items.append(payment)
        return payment


class FakeStorage:
    async def save(self, file, folder: str, max_size_bytes: int, allowed_types=None) -> StoredFile:
        return StoredFile(
            path=f"{folder}/fake.pdf",
            original_name=file.name,
            size=100,
            content_type="application/pdf",
        )


class FakeUpload:
    def __init__(self, name: str) -> None:
        self.name = name


def make_user(user_id: int, role: UserRole) -> User:
    user = User(email=f"u{user_id}@example.com", password_hash="x", full_name="Имя", phone="+79990000000", role=role)
    user.id = user_id
    return user


def make_usecase(
    experts: list[User], price: Decimal | None = Decimal("20000")
) -> tuple[CreateExpertiseUseCase, FakeExpertiseRepository, FakeNotificationRepository]:
    expertises = FakeExpertiseRepository()
    notifications = FakeNotificationRepository()
    usecase = CreateExpertiseUseCase(
        expertises, FakeProfileRepository(experts), notifications, FakeTariffRepository(price), FakeStorage()
    )
    return usecase, expertises, notifications


FITTING = [ExpertCertificate(area_code="Э4", object_code="kl", category=1, valid_until=date(2030, 1, 1))]


def make_expertise(status: ExpertiseStatus, price: Decimal | None = Decimal("20001")) -> Expertise:
    expertise = Expertise(
        customer_id=1, object_code="kl", area_code="Э4", expert_category=2, status=status, price=price
    )
    expertise.id = 1
    return expertise


def test_resolve_category_prefers_hazard_class() -> None:
    assert resolve_category(1, None) == 1
    assert resolve_category(2, None) == 2
    assert resolve_category(4, None) == 3
    assert resolve_category(4, 1) == 3
    assert resolve_category(None, 2) == 2

    with pytest.raises(InvalidExpertiseError):
        resolve_category(None, None)

    with pytest.raises(InvalidExpertiseError):
        resolve_category(None, 5)


def test_validate_pair() -> None:
    validate_pair("kl_tp", "Э1")
    validate_pair("kl", "Э4")

    with pytest.raises(InvalidExpertiseError):
        validate_pair("kl", "Э1")

    with pytest.raises(InvalidExpertiseError):
        validate_pair("d", "Э1")


def test_split_price_puts_kopeck_into_final() -> None:
    assert split_price(Decimal("20000")) == (Decimal("10000.00"), Decimal("10000.00"))
    assert split_price(Decimal("20001")) == (Decimal("10000.50"), Decimal("10000.50"))
    assert split_price(Decimal("0.03")) == (Decimal("0.02"), Decimal("0.01"))


def test_create_saves_documents_price_and_notifies_experts() -> None:
    expert = make_user(10, UserRole.EXPERT)
    usecase, expertises, notifications = make_usecase([expert])
    customer = make_user(1, UserRole.CUSTOMER)
    data = ExpertiseInSchema(object_code="kl_tp", area_code="Э1", hazard_class=2, comment="  срочно ")

    created = asyncio.run(usecase.execute(customer, data, [FakeUpload("a.pdf"), FakeUpload("b.pdf")]))

    expertise = created.expertise
    assert expertise.id == 1
    assert expertise.customer_id == 1
    assert expertise.expert_category == 2
    assert expertise.comment == "срочно"
    assert expertise.status == ExpertiseStatus.NEW
    assert expertise.price == Decimal("20000")
    assert len(expertise.documents) == 2
    assert expertise.documents[0].original_name == "a.pdf"
    assert created.notified_experts == [expert]
    assert len(notifications.added) == 1
    assert notifications.added[0].user_id == 10


def test_create_without_tariff_keeps_price_empty() -> None:
    usecase, expertises, notifications = make_usecase([], price=None)
    data = ExpertiseInSchema(object_code="kl_tp", area_code="Э1", expert_category=1)

    created = asyncio.run(usecase.execute(make_user(1, UserRole.CUSTOMER), data, [FakeUpload("a.pdf")]))

    assert created.expertise.price is None


def test_create_requires_files() -> None:
    usecase, expertises, notifications = make_usecase([])
    data = ExpertiseInSchema(object_code="kl_tp", area_code="Э1", expert_category=1)

    with pytest.raises(InvalidExpertiseError):
        asyncio.run(usecase.execute(make_user(1, UserRole.CUSTOMER), data, []))


def test_certificate_fits_by_category() -> None:
    expertise = Expertise(customer_id=1, object_code="d", area_code="Э4", expert_category=2)
    strong = ExpertCertificate(area_code="Э4", object_code="d", category=1, valid_until=date(2030, 1, 1))
    weak = ExpertCertificate(area_code="Э4", object_code="d", category=3, valid_until=date(2030, 1, 1))
    other = ExpertCertificate(area_code="Э5", object_code="d", category=1, valid_until=date(2030, 1, 1))

    assert certificate_fits([strong], expertise)
    assert not certificate_fits([weak], expertise)
    assert not certificate_fits([other], expertise)


def test_can_view_rules() -> None:
    expertise = Expertise(customer_id=1, object_code="d", area_code="Э4", expert_category=2)
    owner = make_user(1, UserRole.CUSTOMER)
    stranger = make_user(2, UserRole.CUSTOMER)
    expert = make_user(10, UserRole.EXPERT)
    fitting = [ExpertCertificate(area_code="Э4", object_code="d", category=1, valid_until=date(2030, 1, 1))]

    assert can_view(expertise, owner, [])
    assert not can_view(expertise, stranger, [])
    assert can_view(expertise, expert, fitting)
    assert not can_view(expertise, expert, [])

    expertise.expert_id = 10
    assert can_view(expertise, expert, [])
    expertise.expert_id = 11
    assert not can_view(expertise, expert, fitting)


def test_accept_locks_expertise_and_notifies_customer() -> None:
    expertise = make_expertise(ExpertiseStatus.NEW)
    notifications = FakeNotificationRepository()
    usecase = AcceptExpertiseUseCase(
        FakeExpertiseRepository(), FakeProfileRepository([], FITTING), notifications
    )
    expert = make_user(10, UserRole.EXPERT)

    updated = asyncio.run(usecase.execute(expert, expertise))

    assert updated.status == ExpertiseStatus.EXPERT_READY
    assert updated.expert_id == 10
    assert updated.expert_ready_at is not None
    assert notifications.added[0].user_id == 1

    with pytest.raises(ExpertiseStateError):
        asyncio.run(usecase.execute(make_user(11, UserRole.EXPERT), expertise))


def test_accept_requires_fitting_certificate_and_price() -> None:
    expert = make_user(10, UserRole.EXPERT)

    no_certificates = AcceptExpertiseUseCase(
        FakeExpertiseRepository(), FakeProfileRepository([], []), FakeNotificationRepository()
    )
    with pytest.raises(ExpertiseAccessError):
        asyncio.run(no_certificates.execute(expert, make_expertise(ExpertiseStatus.NEW)))

    no_price = AcceptExpertiseUseCase(
        FakeExpertiseRepository(), FakeProfileRepository([], FITTING), FakeNotificationRepository()
    )
    with pytest.raises(PriceMissingError):
        asyncio.run(no_price.execute(expert, make_expertise(ExpertiseStatus.NEW, price=None)))


def test_confirm_makes_contract_and_notifies_expert() -> None:
    expertise = make_expertise(ExpertiseStatus.EXPERT_READY)
    expertise.expert_id = 10
    notifications = FakeNotificationRepository()
    usecase = ConfirmExpertiseUseCase(FakeExpertiseRepository(), notifications)

    with pytest.raises(ExpertiseAccessError):
        asyncio.run(usecase.execute(make_user(2, UserRole.CUSTOMER), expertise))

    updated = asyncio.run(usecase.execute(make_user(1, UserRole.CUSTOMER), expertise))

    assert updated.status == ExpertiseStatus.CONTRACT
    assert updated.contract_at is not None
    assert notifications.added[0].user_id == 10

    with pytest.raises(ExpertiseStateError):
        asyncio.run(usecase.execute(make_user(1, UserRole.CUSTOMER), expertise))


def test_payment_stage_amounts_and_reuse() -> None:
    expertise = make_expertise(ExpertiseStatus.CONTRACT)
    expertise.expert_id = 10
    payments = FakePaymentRepository()
    create_payment = FakeCreatePayment(payments)
    usecase = CreateExpertisePaymentUseCase(FakeExpertiseRepository(), payments, create_payment)
    customer = make_user(1, UserRole.CUSTOMER)

    advance = asyncio.run(usecase.execute(customer, expertise))

    assert advance.amount == Decimal("10000.50")
    assert expertise.advance_payment_id == advance.id
    assert "аванс" in create_payment.calls[0][1]

    again = asyncio.run(usecase.execute(customer, expertise))
    assert again.id == advance.id
    assert len(create_payment.calls) == 1

    expertise.status = ExpertiseStatus.CONCLUSION_READY
    final = asyncio.run(usecase.execute(customer, expertise))

    assert final.amount == Decimal("10000.50")
    assert expertise.final_payment_id == final.id
    assert "остаток" in create_payment.calls[1][1]

    expertise.status = ExpertiseStatus.IN_PROGRESS
    with pytest.raises(ExpertiseStateError):
        asyncio.run(usecase.execute(customer, expertise))


def test_apply_payment_moves_status_once() -> None:
    expertise = make_expertise(ExpertiseStatus.CONTRACT)
    expertise.expert_id = 10
    expertise.advance_payment_id = 5
    expertises = FakeExpertiseRepository()
    expertises.items.append(expertise)
    notifications = FakeNotificationRepository()
    usecase = ApplyExpertisePaymentUseCase(expertises, notifications)

    pending = Payment(user_id=1, amount=Decimal("1"), description="x", status=PaymentStatus.PENDING, provider_payment_id="a")
    pending.id = 5
    assert asyncio.run(usecase.execute(pending)) is None

    paid = Payment(user_id=1, amount=Decimal("1"), description="x", status=PaymentStatus.SUCCEEDED, provider_payment_id="a")
    paid.id = 5
    updated = asyncio.run(usecase.execute(paid))

    assert updated is not None
    assert updated.status == ExpertiseStatus.IN_PROGRESS
    assert updated.advance_paid_at is not None
    assert len(notifications.added) == 1

    asyncio.run(usecase.execute(paid))
    assert len(notifications.added) == 1

    expertise.status = ExpertiseStatus.CONCLUSION_READY
    expertise.final_payment_id = 6
    final = Payment(user_id=1, amount=Decimal("1"), description="x", status=PaymentStatus.SUCCEEDED, provider_payment_id="b")
    final.id = 6
    updated = asyncio.run(usecase.execute(final))

    assert updated is not None
    assert updated.status == ExpertiseStatus.PAID
    assert updated.final_paid_at is not None


def test_remarks_cycle_returns_expertise_to_work() -> None:
    expertise = make_expertise(ExpertiseStatus.IN_PROGRESS)
    expertise.expert_id = 10
    expert = make_user(10, UserRole.EXPERT)
    customer = make_user(1, UserRole.CUSTOMER)
    notifications = FakeNotificationRepository()
    repo = FakeExpertiseRepository()

    remarks = SendRemarksUseCase(repo, notifications, FakeStorage())
    revision = ResubmitDocumentationUseCase(repo, notifications, FakeStorage())

    with pytest.raises(ExpertiseAccessError):
        asyncio.run(remarks.execute(make_user(11, UserRole.EXPERT), expertise, "текст", []))

    with pytest.raises(InvalidExpertiseError):
        asyncio.run(remarks.execute(expert, expertise, "   ", []))

    asyncio.run(remarks.execute(expert, expertise, "  Уточните раздел 3  ", [FakeUpload("r.pdf")]))

    assert expertise.status == ExpertiseStatus.REMARKS
    assert len(expertise.remarks) == 1
    assert expertise.remarks[0].text == "Уточните раздел 3"
    assert expertise.remarks[0].documents[0].kind == "remarks"
    assert notifications.added[0].user_id == 1

    with pytest.raises(InvalidExpertiseError):
        asyncio.run(revision.execute(customer, expertise, None, []))

    asyncio.run(revision.execute(customer, expertise, "  Исправил раздел 3  ", [FakeUpload("fixed.pdf")]))

    assert expertise.status == ExpertiseStatus.IN_PROGRESS
    assert expertise.remarks[0].resolved_at is not None
    assert expertise.remarks[0].response_text == "Исправил раздел 3"
    assert expertise.documents[-1].kind == "revision"
    assert expertise.remarks[0].documents[-1].kind == "revision"
    assert notifications.added[1].user_id == 10

    with pytest.raises(ExpertiseStateError):
        asyncio.run(revision.execute(customer, expertise, None, [FakeUpload("again.pdf")]))

    asyncio.run(remarks.execute(expert, expertise, None, [FakeUpload("r2.pdf")]))

    assert len(expertise.remarks) == 2
    assert expertise.remarks[1].text is None


def test_conclusion_ready_send_and_accept_work() -> None:
    expertise = make_expertise(ExpertiseStatus.IN_PROGRESS)
    expertise.expert_id = 10
    expert = make_user(10, UserRole.EXPERT)
    customer = make_user(1, UserRole.CUSTOMER)
    notifications = FakeNotificationRepository()
    repo = FakeExpertiseRepository()

    ready = MarkConclusionReadyUseCase(repo, notifications)
    with pytest.raises(ExpertiseAccessError):
        asyncio.run(ready.execute(make_user(11, UserRole.EXPERT), expertise))
    asyncio.run(ready.execute(expert, expertise))
    assert expertise.status == ExpertiseStatus.CONCLUSION_READY

    send = SendConclusionUseCase(repo, notifications, FakeStorage())
    with pytest.raises(ExpertiseStateError):
        asyncio.run(send.execute(expert, expertise, ExpertiseResult.POSITIVE, [FakeUpload("c.pdf")]))

    expertise.status = ExpertiseStatus.PAID
    with pytest.raises(InvalidExpertiseError):
        asyncio.run(send.execute(expert, expertise, "weird", [FakeUpload("c.pdf")]))
    with pytest.raises(InvalidExpertiseError):
        asyncio.run(send.execute(expert, expertise, ExpertiseResult.POSITIVE, []))

    asyncio.run(send.execute(expert, expertise, ExpertiseResult.NEGATIVE, [FakeUpload("c.pdf")]))
    assert expertise.status == ExpertiseStatus.SENT
    assert expertise.result == ExpertiseResult.NEGATIVE
    assert expertise.documents[0].kind == "conclusion"

    accept = AcceptWorkUseCase(repo, notifications)
    asyncio.run(accept.execute(customer, expertise))
    assert expertise.status == ExpertiseStatus.ACCEPTED
    assert expertise.accepted_at is not None

    recipients = [item.user_id for item in notifications.added]
    assert recipients == [1, 1, 10]
