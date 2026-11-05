"""Зависимости оплаты."""

from collections.abc import AsyncIterator

import httpx
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.audit_payment_confirmation import AuditPaymentConfirmation
from src.audit.repositories.audit_payments import AuditPaymentRepository
from src.audit.repositories.audits import AuditRepository
from src.core.database import get_session
from src.core.settings import Settings, get_settings
from src.expertise.expertise_payment_confirmation import ExpertisePaymentConfirmation
from src.expertise.repositories.expertise_payments import ExpertisePaymentRepository
from src.expertise.repositories.expertises import ExpertiseRepository
from src.notifications.repositories.notifications import NotificationRepository
from src.payments.exceptions import PaymentConfigurationError
from src.payments.gateway import YooKassaGateway
from src.payments.options import PAYMENT_TIMEOUT_SECONDS, YOOKASSA_API_URL
from src.payments.payment_creator import PaymentCreator
from src.payments.payment_status_updater import PaymentStatusUpdater
from src.payments.repositories.payments import PaymentRepository


def get_audit_payment_confirmation(*, session: AsyncSession) -> AuditPaymentConfirmation:
    """Учёт оплаты аудита."""

    return AuditPaymentConfirmation(
        audits=AuditRepository(session=session),
        stages=AuditPaymentRepository(session=session),
        notifications=NotificationRepository(session=session),
    )


def get_expertise_payment_confirmation(*, session: AsyncSession) -> ExpertisePaymentConfirmation:
    """Учёт оплаты экспертизы."""

    return ExpertisePaymentConfirmation(
        expertises=ExpertiseRepository(session=session),
        stages=ExpertisePaymentRepository(session=session),
        notifications=NotificationRepository(session=session),
    )


async def get_payment_gateway(
    *,
    settings: Settings = Depends(get_settings),
) -> AsyncIterator[YooKassaGateway]:
    """Открыть соединение с провайдером."""

    if not settings.yookassa_shop_id or not settings.yookassa_secret_key:
        raise PaymentConfigurationError()

    async with httpx.AsyncClient(
        base_url=YOOKASSA_API_URL,
        auth=(settings.yookassa_shop_id, settings.yookassa_secret_key),
        timeout=PAYMENT_TIMEOUT_SECONDS,
    ) as client:
        yield YooKassaGateway(
            client=client,
            vat_code=settings.yookassa_vat_code,
        )


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
