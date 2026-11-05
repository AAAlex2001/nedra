"""Зависимости оплаты картой."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.expertise.repositories.expertise_payments import ExpertisePaymentRepository
from src.expertise.repositories.expertises import ExpertiseRepository
from src.expertise.site.usecases.create_payment import CreateExpertisePaymentUseCase
from src.payments.dependencies import get_expertise_payment_confirmation, get_payment_creator
from src.payments.payment_creator import PaymentCreator
from src.payments.repositories.payments import PaymentRepository


def get_create_expertise_payment_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    creator: PaymentCreator = Depends(get_payment_creator),
) -> CreateExpertisePaymentUseCase:
    """Оплата этапа экспертизы."""

    return CreateExpertisePaymentUseCase(
        session=session,
        expertises=ExpertiseRepository(session=session),
        stages=ExpertisePaymentRepository(session=session),
        payments=PaymentRepository(session=session),
        creator=creator,
        confirmation=get_expertise_payment_confirmation(session=session),
    )
