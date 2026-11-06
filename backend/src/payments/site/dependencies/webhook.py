"""Уведомления платёжного провайдера."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.payments.dependencies.confirmation import (
    get_audit_payment_confirmation,
    get_expertise_payment_confirmation,
)
from src.payments.dependencies.payments import get_payment_status_updater
from src.payments.payment_status_updater import PaymentStatusUpdater
from src.payments.repositories.payments import PaymentRepository
from src.payments.site.usecases.process_webhook import ProcessPaymentWebhookUseCase


def get_process_payment_webhook_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    status_updater: PaymentStatusUpdater = Depends(get_payment_status_updater),
) -> ProcessPaymentWebhookUseCase:
    """Обработка уведомления провайдера."""

    return ProcessPaymentWebhookUseCase(
        session=session,
        payments=PaymentRepository(session=session),
        status_updater=status_updater,
        audit_confirmation=get_audit_payment_confirmation(session=session),
        expertise_confirmation=get_expertise_payment_confirmation(session=session),
    )
