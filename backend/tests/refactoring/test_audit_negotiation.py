"""Согласование стоимости аудита."""

import asyncio
import os
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest
from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.audit.enums import AuditOfferAnswer, AuditStatus
from src.audit.exceptions import (
    AuditNotFoundError,
    AuditStateError,
    InvalidAuditPriceError,
)
from src.audit.models.audit import Audit
from src.audit.site.dependencies.price import (
    get_answer_audit_counter_offer_usecase,
    get_answer_audit_offer_usecase,
    get_propose_audit_price_usecase,
)
from src.audit.site.schemas.answer_audit_offer import (
    AnswerAuditOfferRequest,
    AnswerAuditOfferResponse,
)
from src.core.settings import Settings
from src.notifications.models.notification import Notification
from src.users.models.user import User


@pytest.fixture
async def offered_audit(
    *, session_factory: async_sessionmaker, settings: Settings, audit_ids: tuple[int, int, int]
) -> tuple[int, int, int]:
    """Предложить цену по новой заявке."""

    audit_id, _, lead_id = audit_ids
    async with session_factory() as session:
        audit = await session.get(Audit, audit_id)
        audit.customer_budget = Decimal("120000")
        await session.commit()

    async with session_factory() as session:
        user = await session.get(User, lead_id)
        usecase = get_propose_audit_price_usecase(session=session, settings=settings)
        await usecase.execute(user=user, audit_id=audit_id, price=Decimal("150000"))

    return audit_ids


@pytest.mark.parametrize(
    ("answer", "expected_status"),
    [
        (AuditOfferAnswer.ACCEPT, AuditStatus.EXPERT_READY),
        (AuditOfferAnswer.COUNTER, AuditStatus.COUNTER),
        (AuditOfferAnswer.DECLINE, AuditStatus.NEW),
    ],
)
async def test_customer_answer(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    offered_audit: tuple[int, int, int],
    answer: AuditOfferAnswer,
    expected_status: AuditStatus,
) -> None:
    """Сохранить ответ заказчика и уведомить аудитора."""

    audit_id, customer_id, lead_id = offered_audit
    async with session_factory() as session:
        user = await session.get(User, customer_id)
        usecase = get_answer_audit_offer_usecase(session=session, settings=settings)
        result = await usecase.execute(
            user=user,
            audit_id=audit_id,
            answer=answer,
            price=Decimal("130000"),
        )

    assert result.status == expected_status
    async with session_factory() as session:
        audit = await session.get(Audit, audit_id)
        notification = await session.scalar(select(Notification).order_by(Notification.id.desc()))

        assert audit.status == expected_status
        assert audit.customer_budget == Decimal("120000")
        assert notification.user_id == lead_id

        if answer == AuditOfferAnswer.ACCEPT:
            assert audit.agreed_price == Decimal("150000")
            assert audit.offer_price is None
            assert audit.counter_price is None
            assert audit.lead_ready_at is not None
        elif answer == AuditOfferAnswer.COUNTER:
            assert audit.counter_price == Decimal("130000")
            assert audit.offer_price == Decimal("150000")
            assert audit.agreed_price is None
        else:
            assert audit.lead_id is None
            assert audit.offer_price is None
            assert audit.counter_price is None
            assert audit.agreed_price is None
            assert audit.lead_ready_at is None


@pytest.mark.parametrize("price", [None, Decimal("99999"), Decimal("150000"), Decimal("160000")])
async def test_invalid_counter_price_keeps_offer(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    offered_audit: tuple[int, int, int],
    price: Decimal | None,
) -> None:
    """Оставить предложение без изменений при неверной цене."""

    audit_id, customer_id, _ = offered_audit
    async with session_factory() as session:
        user = await session.get(User, customer_id)
        usecase = get_answer_audit_offer_usecase(session=session, settings=settings)

        with pytest.raises(InvalidAuditPriceError):
            await usecase.execute(
                user=user,
                audit_id=audit_id,
                answer=AuditOfferAnswer.COUNTER,
                price=price,
            )

    async with session_factory() as session:
        audit = await session.get(Audit, audit_id)
        assert audit.status == AuditStatus.OFFER
        assert audit.counter_price is None
        assert await session.scalar(select(func.count()).select_from(Notification)) == 1


@pytest.mark.parametrize("accept", [True, False])
async def test_lead_answers_counter_offer(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    offered_audit: tuple[int, int, int],
    accept: bool,
) -> None:
    """Завершить переговоры по встречной цене."""

    audit_id, customer_id, lead_id = offered_audit
    async with session_factory() as session:
        customer = await session.get(User, customer_id)
        answer_offer = get_answer_audit_offer_usecase(session=session, settings=settings)
        await answer_offer.execute(
            user=customer,
            audit_id=audit_id,
            answer=AuditOfferAnswer.COUNTER,
            price=Decimal("130000"),
        )

    async with session_factory() as session:
        lead = await session.get(User, lead_id)
        answer_counter = get_answer_audit_counter_offer_usecase(session=session, settings=settings)
        result = await answer_counter.execute(user=lead, audit_id=audit_id, accept=accept)

    async with session_factory() as session:
        audit = await session.get(Audit, audit_id)
        notification = await session.scalar(select(Notification).order_by(Notification.id.desc()))

        assert notification.user_id == customer_id
        assert audit.customer_budget == Decimal("120000")
        assert audit.offer_price is None
        assert audit.counter_price is None

        if accept:
            assert result.status == AuditStatus.EXPERT_READY
            assert audit.agreed_price == Decimal("130000")
            assert audit.lead_id == lead_id
        else:
            assert result.status == AuditStatus.NEW
            assert audit.agreed_price is None
            assert audit.lead_id is None


async def test_other_customer_cannot_answer(
    *, session_factory: async_sessionmaker, settings: Settings, offered_audit: tuple[int, int, int]
) -> None:
    """Скрыть чужую заявку от заказчика."""

    audit_id, _, _ = offered_audit
    stranger = User(id=9876, role="customer")
    async with session_factory() as session:
        usecase = get_answer_audit_offer_usecase(session=session, settings=settings)

        with pytest.raises(AuditNotFoundError):
            await usecase.execute(user=stranger, audit_id=audit_id, answer=AuditOfferAnswer.ACCEPT)


async def test_notification_error_rolls_back_answer(
    *, session_factory: async_sessionmaker, settings: Settings, offered_audit: tuple[int, int, int]
) -> None:
    """Откатить ответ при ошибке уведомления."""

    audit_id, customer_id, _ = offered_audit
    async with session_factory() as session:
        customer = await session.get(User, customer_id)
        usecase = get_answer_audit_offer_usecase(session=session, settings=settings)
        usecase.notifications.add = AsyncMock(side_effect=RuntimeError("Ошибка сохранения"))
        usecase.letters.sender.send = AsyncMock()

        with pytest.raises(RuntimeError):
            await usecase.execute(user=customer, audit_id=audit_id, answer=AuditOfferAnswer.ACCEPT)

        await session.rollback()
        usecase.letters.sender.send.assert_not_awaited()

    async with session_factory() as session:
        audit = await session.get(Audit, audit_id)
        assert audit.status == AuditStatus.OFFER
        assert audit.agreed_price is None
        assert await session.scalar(select(func.count()).select_from(Notification)) == 1


@pytest.mark.skipif(
    not os.environ.get("NEDRA_TEST_DATABASE_URL"), reason="Нужна тестовая PostgreSQL"
)
async def test_conflicting_answers_are_serialized(
    *, session_factory: async_sessionmaker, settings: Settings, offered_audit: tuple[int, int, int]
) -> None:
    """Сохранить только один из одновременных ответов."""

    audit_id, customer_id, _ = offered_audit

    async def answer_offer(*, answer: AuditOfferAnswer) -> AnswerAuditOfferResponse:
        """Ответить в отдельной транзакции."""

        async with session_factory() as session:
            customer = await session.get(User, customer_id)
            usecase = get_answer_audit_offer_usecase(session=session, settings=settings)

            return await usecase.execute(user=customer, audit_id=audit_id, answer=answer)

    results = await asyncio.gather(
        answer_offer(answer=AuditOfferAnswer.ACCEPT),
        answer_offer(answer=AuditOfferAnswer.DECLINE),
        return_exceptions=True,
    )

    assert sum(isinstance(result, AnswerAuditOfferResponse) for result in results) == 1
    assert sum(isinstance(result, AuditStateError) for result in results) == 1

    async with session_factory() as session:
        assert await session.scalar(select(func.count()).select_from(Notification)) == 2


@pytest.mark.parametrize("payload", [{"answer": "unknown"}, {"answer": "counter"}])
def test_invalid_answer_request(*, payload: dict) -> None:
    """Отклонить неизвестный ответ и встречное предложение без суммы."""

    with pytest.raises(ValidationError):
        AnswerAuditOfferRequest.model_validate(payload)
