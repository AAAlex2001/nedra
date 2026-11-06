"""Учёт оплаты услуг."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.audit_payment_confirmation import AuditPaymentConfirmation
from src.audit.repositories.audit_payments import AuditPaymentRepository
from src.audit.repositories.audits import AuditRepository
from src.expertise.expertise_payment_confirmation import ExpertisePaymentConfirmation
from src.expertise.repositories.expertise_payments import ExpertisePaymentRepository
from src.expertise.repositories.expertises import ExpertiseRepository
from src.notifications.repositories.notifications import NotificationRepository


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
