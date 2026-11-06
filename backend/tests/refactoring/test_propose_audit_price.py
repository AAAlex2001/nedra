"""Проверка предложения стоимости аудита."""

import asyncio
import os
from decimal import Decimal
from unittest.mock import AsyncMock

import aiosmtplib
import pytest
from fastapi import FastAPI
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from starlette.requests import Request

from src.audit.enums import AuditStatus
from src.audit.exceptions import (
    AuditAccessError,
    AuditNotFoundError,
    AuditStateError,
    InvalidAuditPriceError,
)
from src.audit.models.audit import Audit
from src.audit.site.dependencies.price import get_propose_audit_price_usecase
from src.audit.site.schemas.propose_audit_price import ProposeAuditPriceResponse
from src.core.database import get_session
from src.core.settings import Settings
from src.notifications.models.notification import Notification
from src.users.enums import UserRole
from src.users.models.expert_profile import ExpertProfile
from src.users.models.user import User


async def test_price_and_notification_are_committed(
    *, session_factory: async_sessionmaker, settings: Settings, audit_ids: tuple[int, int, int]
) -> None:
    """Сохранить предложение и уведомление вместе."""

    audit_id, customer_id, lead_id = audit_ids
    async with session_factory() as session:
        user = await session.get(User, lead_id)
        usecase = get_propose_audit_price_usecase(session=session, settings=settings)
        result = await usecase.execute(user=user, audit_id=audit_id, price=Decimal("150000.00"))

    async with session_factory() as session:
        audit = await session.get(Audit, audit_id)
        notification = await session.scalar(select(Notification))

        assert result.status == AuditStatus.OFFER
        assert audit.offer_price == Decimal("150000.00")
        assert audit.lead_id == lead_id
        assert notification.user_id == customer_id
        assert notification.audit_id == audit_id
        assert "150 000,00" in notification.text


@pytest.mark.parametrize("price", ["99999.99", "100000000", "100000.001", "NaN", "Infinity"])
async def test_invalid_price_does_not_change_audit(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    audit_ids: tuple[int, int, int],
    price: str,
) -> None:
    """Отклонить некорректную сумму без изменения заявки."""

    audit_id, _, lead_id = audit_ids
    async with session_factory() as session:
        user = await session.get(User, lead_id)
        usecase = get_propose_audit_price_usecase(session=session, settings=settings)

        with pytest.raises(InvalidAuditPriceError):
            await usecase.execute(user=user, audit_id=audit_id, price=Decimal(price))

    async with session_factory() as session:
        audit = await session.get(Audit, audit_id)
        assert audit.status == AuditStatus.NEW
        assert audit.lead_id is None
        assert await session.scalar(select(func.count()).select_from(Notification)) == 0


async def test_customer_cannot_propose_price(
    *, session_factory: async_sessionmaker, settings: Settings, audit_ids: tuple[int, int, int]
) -> None:
    """Запретить заказчику действие руководителя группы."""

    audit_id, customer_id, _ = audit_ids
    async with session_factory() as session:
        user = await session.get(User, customer_id)
        usecase = get_propose_audit_price_usecase(session=session, settings=settings)

        with pytest.raises(AuditAccessError):
            await usecase.execute(user=user, audit_id=audit_id, price=Decimal("150000"))


async def test_expert_without_lead_permission_cannot_propose_price(
    *, session_factory: async_sessionmaker, settings: Settings, audit_ids: tuple[int, int, int]
) -> None:
    """Проверить право руководить аудиторской группой."""

    audit_id, _, lead_id = audit_ids
    async with session_factory() as session:
        profile = await session.get(ExpertProfile, lead_id)
        profile.audit_lead = False
        await session.commit()

    async with session_factory() as session:
        user = await session.get(User, lead_id)
        usecase = get_propose_audit_price_usecase(session=session, settings=settings)

        with pytest.raises(AuditAccessError):
            await usecase.execute(user=user, audit_id=audit_id, price=Decimal("150000"))


async def test_fixed_budget_cannot_be_changed(
    *, session_factory: async_sessionmaker, settings: Settings, audit_ids: tuple[int, int, int]
) -> None:
    """Запретить торг при фиксированном бюджете."""

    audit_id, _, lead_id = audit_ids
    async with session_factory() as session:
        audit = await session.get(Audit, audit_id)
        audit.customer_budget = Decimal("100000")
        audit.negotiation_allowed = False
        await session.commit()

    async with session_factory() as session:
        user = await session.get(User, lead_id)
        usecase = get_propose_audit_price_usecase(session=session, settings=settings)

        with pytest.raises(AuditStateError):
            await usecase.execute(user=user, audit_id=audit_id, price=Decimal("150000"))


async def test_repeated_offer_does_not_create_second_notification(
    *, session_factory: async_sessionmaker, settings: Settings, audit_ids: tuple[int, int, int]
) -> None:
    """Отклонить повторное предложение стоимости."""

    audit_id, _, lead_id = audit_ids
    async with session_factory() as session:
        user = await session.get(User, lead_id)
        usecase = get_propose_audit_price_usecase(session=session, settings=settings)
        await usecase.execute(user=user, audit_id=audit_id, price=Decimal("150000"))

    async with session_factory() as session:
        user = await session.get(User, lead_id)
        usecase = get_propose_audit_price_usecase(session=session, settings=settings)

        with pytest.raises(AuditStateError):
            await usecase.execute(user=user, audit_id=audit_id, price=Decimal("160000"))

    async with session_factory() as session:
        assert await session.scalar(select(func.count()).select_from(Notification)) == 1


async def test_notification_failure_rolls_back_offer(
    *, session_factory: async_sessionmaker, settings: Settings, audit_ids: tuple[int, int, int]
) -> None:
    """Откатить цену при ошибке сохранения уведомления."""

    audit_id, _, lead_id = audit_ids
    app = FastAPI()
    app.state.session_factory = session_factory
    request = Request({"type": "http", "app": app})
    dependency = get_session(request=request)
    session: AsyncSession = await anext(dependency)
    user = await session.get(User, lead_id)
    usecase = get_propose_audit_price_usecase(session=session, settings=settings)
    usecase.notifications.add = AsyncMock(side_effect=RuntimeError("Ошибка сохранения"))
    usecase.letters.sender.send = AsyncMock()

    try:
        with pytest.raises(RuntimeError) as caught:
            await usecase.execute(user=user, audit_id=audit_id, price=Decimal("150000"))

        with pytest.raises(RuntimeError):
            await dependency.athrow(caught.value)
    finally:
        await dependency.aclose()

    usecase.letters.sender.send.assert_not_awaited()
    async with session_factory() as session:
        audit = await session.get(Audit, audit_id)
        assert audit.status == AuditStatus.NEW
        assert audit.offer_price is None
        assert audit.lead_id is None
        assert await session.scalar(select(func.count()).select_from(Notification)) == 0


async def test_smtp_failure_keeps_committed_offer(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    audit_ids: tuple[int, int, int],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Сохранить результат при недоступности почты."""

    audit_id, _, lead_id = audit_ids
    settings.smtp_host = "smtp.example.com"
    settings.smtp_user = "noreply@example.com"
    smtp_send = AsyncMock(side_effect=aiosmtplib.SMTPException("Недоступна почта"))
    monkeypatch.setattr(aiosmtplib, "send", smtp_send)

    async with session_factory() as session:
        user = await session.get(User, lead_id)
        usecase = get_propose_audit_price_usecase(session=session, settings=settings)
        result = await usecase.execute(user=user, audit_id=audit_id, price=Decimal("150000"))

    assert result.status == AuditStatus.OFFER
    smtp_send.assert_awaited_once()
    async with session_factory() as session:
        audit = await session.get(Audit, audit_id)
        assert audit.status == AuditStatus.OFFER
        assert await session.scalar(select(func.count()).select_from(Notification)) == 1


@pytest.mark.skipif(
    not os.environ.get("NEDRA_TEST_DATABASE_URL"), reason="Нужна тестовая PostgreSQL"
)
async def test_concurrent_leads_cannot_both_take_audit(
    *, session_factory: async_sessionmaker, settings: Settings, audit_ids: tuple[int, int, int]
) -> None:
    """Принять только одно из одновременных предложений."""

    audit_id, _, lead_id = audit_ids
    async with session_factory() as session:
        second_lead = User(
            email="second-lead@example.com",
            password_hash="unused",
            full_name="Второй руководитель",
            phone="+79990000003",
            role=UserRole.EXPERT,
        )
        session.add(second_lead)
        await session.flush()
        session.add(ExpertProfile(user_id=second_lead.id, audit_lead=True, directions=["audit"]))
        await session.commit()
        second_lead_id = second_lead.id

    async def propose(*, user_id: int) -> ProposeAuditPriceResponse:
        """Предложить цену в отдельной транзакции."""

        async with session_factory() as session:
            user = await session.get(User, user_id)
            usecase = get_propose_audit_price_usecase(session=session, settings=settings)

            return await usecase.execute(user=user, audit_id=audit_id, price=Decimal("150000"))

    results = await asyncio.gather(
        propose(user_id=lead_id),
        propose(user_id=second_lead_id),
        return_exceptions=True,
    )
    assert sum(isinstance(result, ProposeAuditPriceResponse) for result in results) == 1
    assert sum(isinstance(result, AuditNotFoundError) for result in results) == 1

    async with session_factory() as session:
        assert await session.scalar(select(func.count()).select_from(Notification)) == 1
