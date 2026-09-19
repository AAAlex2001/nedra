"""Платежи: репозиторий, шлюз ЮKassa и фабрики сценариев."""

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_session
from app.services.payments.gateway import YooKassaGateway
from app.services.payments.repo import PaymentRepository
from app.services.payments.usecases.create_payment import CreatePaymentUseCase
from app.services.payments.usecases.sync_payment_status import SyncPaymentStatusUseCase


def get_payment_repository(
    session: AsyncSession = Depends(get_session),
) -> PaymentRepository:
    """Репозиторий платежей с сессией текущего запроса."""

    return PaymentRepository(session)


def get_payment_gateway() -> YooKassaGateway:
    """Шлюз ЮKassa. Без ключей в окружении платежи отключены — отвечаем 503."""

    settings = get_settings()

    if not settings.yookassa_shop_id or not settings.yookassa_secret_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Оплата не настроена",
        )

    return YooKassaGateway(
        settings.yookassa_shop_id, settings.yookassa_secret_key, settings.yookassa_vat_code
    )


def get_create_payment_usecase(
    payments: PaymentRepository = Depends(get_payment_repository),
    gateway: YooKassaGateway = Depends(get_payment_gateway),
) -> CreatePaymentUseCase:
    """Сценарий создания платежа."""

    settings = get_settings()

    if not settings.payment_return_url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Не задан адрес возврата после оплаты",
        )

    return CreatePaymentUseCase(payments, gateway, settings.payment_return_url)


def get_sync_payment_usecase(
    payments: PaymentRepository = Depends(get_payment_repository),
    gateway: YooKassaGateway = Depends(get_payment_gateway),
) -> SyncPaymentStatusUseCase:
    """Сценарий синхронизации статуса."""

    return SyncPaymentStatusUseCase(payments, gateway)
