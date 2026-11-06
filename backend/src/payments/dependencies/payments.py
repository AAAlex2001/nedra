"""Зависимости оплаты."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.core.settings import Settings, get_settings
from src.payments.dependencies.gateway import get_payment_gateway
from src.payments.exceptions import PaymentConfigurationError
from src.payments.gateway import YooKassaGateway
from src.payments.payment_creator import PaymentCreator
from src.payments.payment_status_updater import PaymentStatusUpdater
from src.payments.repositories.payments import PaymentRepository


def get_payment_creator(
    *,
    session: AsyncSession = Depends(get_session),
    gateway: YooKassaGateway = Depends(get_payment_gateway),
    settings: Settings = Depends(get_settings),
) -> PaymentCreator:
    """Создание платежа у провайдера."""

    if not settings.payment_return_url:
        raise PaymentConfigurationError()

    return PaymentCreator(
        payments=PaymentRepository(session=session),
        gateway=gateway,
        return_url=settings.payment_return_url,
    )


def get_payment_status_updater(
    *,
    session: AsyncSession = Depends(get_session),
    gateway: YooKassaGateway = Depends(get_payment_gateway),
) -> PaymentStatusUpdater:
    """Проверка состояния платежа у провайдера."""

    return PaymentStatusUpdater(
        payments=PaymentRepository(session=session),
        gateway=gateway,
    )
