"""Акты выполненных работ."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.repositories.audit_applications import AuditApplicationRepository
from src.audit.repositories.audits import AuditRepository
from src.billing.site.usecases.list_acts import ListActsUseCase
from src.core.database import get_session
from src.expertise.repositories.expertises import ExpertiseRepository


def get_list_acts_usecase(*, session: AsyncSession = Depends(get_session)) -> ListActsUseCase:
    """Просмотр актов заказчика."""

    return ListActsUseCase(
        audits=AuditRepository(session=session),
        applications=AuditApplicationRepository(session=session),
        expertises=ExpertiseRepository(session=session),
    )
