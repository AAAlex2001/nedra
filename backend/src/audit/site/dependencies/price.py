"""Согласование цены."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.repositories.audits import AuditRepository
from src.audit.site.dependencies.letters import get_audit_letters
from src.audit.site.usecases.answer_audit_counter_offer import (
    AnswerAuditCounterOfferUseCase,
)
from src.audit.site.usecases.answer_audit_offer import AnswerAuditOfferUseCase
from src.audit.site.usecases.propose_audit_price import ProposeAuditPriceUseCase
from src.core.database import get_session
from src.core.settings import Settings, get_settings
from src.notifications.repositories.notifications import NotificationRepository
from src.users.repositories.expert_profiles import ExpertProfileRepository
from src.users.repositories.users import UserRepository


def get_propose_audit_price_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> ProposeAuditPriceUseCase:
    """Предложение стоимости аудита."""

    return ProposeAuditPriceUseCase(
        session=session,
        audits=AuditRepository(session=session),
        profiles=ExpertProfileRepository(session=session),
        users=UserRepository(session=session),
        notifications=NotificationRepository(session=session),
        letters=get_audit_letters(settings=settings),
    )


def get_answer_audit_offer_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> AnswerAuditOfferUseCase:
    """Ответ заказчика на цену."""

    return AnswerAuditOfferUseCase(
        session=session,
        audits=AuditRepository(session=session),
        users=UserRepository(session=session),
        notifications=NotificationRepository(session=session),
        letters=get_audit_letters(settings=settings),
    )


def get_answer_audit_counter_offer_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> AnswerAuditCounterOfferUseCase:
    """Ответ аудитора на встречную цену."""

    return AnswerAuditCounterOfferUseCase(
        session=session,
        audits=AuditRepository(session=session),
        users=UserRepository(session=session),
        notifications=NotificationRepository(session=session),
        letters=get_audit_letters(settings=settings),
    )
