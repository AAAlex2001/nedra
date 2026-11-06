"""Просмотр заявок администратором."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.admin.usecases.get_audit import GetAdminAuditUseCase
from src.audit.admin.usecases.get_audit_application import (
    GetAdminAuditApplicationUseCase,
)
from src.audit.admin.usecases.get_audit_contract import GetAdminAuditContractUseCase
from src.audit.admin.usecases.get_audit_customer import GetAdminAuditCustomerUseCase
from src.audit.repositories.audit_applications import AuditApplicationRepository
from src.audit.repositories.audit_customers import AuditCustomerRepository
from src.audit.repositories.audits import AuditRepository
from src.contracts.repositories.contracts import ContractRepository
from src.core.database import get_session
from src.users.repositories.users import UserRepository


def get_audit_usecase(*, session: AsyncSession = Depends(get_session)) -> GetAdminAuditUseCase:
    """Просмотр данных заявки."""

    return GetAdminAuditUseCase(
        audits=AuditRepository(session=session),
    )


def get_audit_customer_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> GetAdminAuditCustomerUseCase:
    """Просмотр данных заявки."""

    return GetAdminAuditCustomerUseCase(
        audits=AuditRepository(session=session),
        customers=AuditCustomerRepository(session=session),
        users=UserRepository(session=session),
    )


def get_audit_application_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> GetAdminAuditApplicationUseCase:
    """Просмотр данных заявки."""

    return GetAdminAuditApplicationUseCase(
        audits=AuditRepository(session=session),
        applications=AuditApplicationRepository(session=session),
    )


def get_audit_contract_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> GetAdminAuditContractUseCase:
    """Просмотр данных заявки."""

    return GetAdminAuditContractUseCase(
        audits=AuditRepository(session=session),
        contracts=ContractRepository(session=session),
    )
