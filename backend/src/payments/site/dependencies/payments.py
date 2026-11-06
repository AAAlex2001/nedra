"""Сценарии оплаты пользователя."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.payments.dependencies.confirmation import (
    get_audit_payment_confirmation,
    get_expertise_payment_confirmation,
)
from src.payments.dependencies.payments import (
    get_payment_creator,
    get_payment_status_updater,
)
from src.payments.payment_creator import PaymentCreator
from src.payments.payment_status_updater import PaymentStatusUpdater
from src.payments.repositories.payments import PaymentRepository
from src.payments.site.usecases.create_payment import CreatePaymentUseCase
from src.payments.site.usecases.get_payment import GetPaymentUseCase
from src.payments.site.usecases.refresh_payment import RefreshPaymentUseCase


def get_create_payment_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    creator: PaymentCreator = Depends(get_payment_creator),
) -> CreatePaymentUseCase:
    """Создание платежа пользователя."""

    return CreatePaymentUseCase(
        session=session,
        creator=creator,
    )


def get_payment_usecase(*, session: AsyncSession = Depends(get_session)) -> GetPaymentUseCase:
    """Просмотр платежа."""

    return GetPaymentUseCase(payments=PaymentRepository(session=session))


def get_refresh_payment_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    status_updater: PaymentStatusUpdater = Depends(get_payment_status_updater),
) -> RefreshPaymentUseCase:
    """Проверка оплаты."""

    return RefreshPaymentUseCase(
        session=session,
        payments=PaymentRepository(session=session),
        status_updater=status_updater,
        audit_confirmation=get_audit_payment_confirmation(session=session),
        expertise_confirmation=get_expertise_payment_confirmation(session=session),
    )
