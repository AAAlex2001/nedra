"""Подробности заявок для администратора."""

from fastapi import APIRouter, Depends

from src.audit.admin.read_dependencies import (
    get_audit_application_usecase,
    get_audit_contract_usecase,
    get_audit_customer_usecase,
    get_audit_usecase,
)
from src.audit.admin.usecases.get_audit import GetAdminAuditUseCase
from src.audit.admin.usecases.get_audit_application import GetAdminAuditApplicationUseCase
from src.audit.admin.usecases.get_audit_contract import GetAdminAuditContractUseCase
from src.audit.admin.usecases.get_audit_customer import GetAdminAuditCustomerUseCase
from src.audit.schemas.audit import AuditResponse
from src.audit.schemas.audit_application import AuditApplicationResponse
from src.audit.schemas.audit_contract import AuditContractResponse
from src.audit.schemas.audit_participants import AuditCustomerResponse
from src.auth.admin.access import require_admin

router = APIRouter(
    prefix="/admin/audits",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)


@router.get("/{audit_id}")
async def get_audit(
    *,
    audit_id: int,
    usecase: GetAdminAuditUseCase = Depends(get_audit_usecase),
) -> AuditResponse:
    """Получить данные заявки."""

    return await usecase.execute(audit_id=audit_id)


@router.get("/{audit_id}/customer")
async def get_audit_customer(
    *,
    audit_id: int,
    usecase: GetAdminAuditCustomerUseCase = Depends(get_audit_customer_usecase),
) -> AuditCustomerResponse:
    """Получить данные заявки."""

    return await usecase.execute(audit_id=audit_id)


@router.get("/{audit_id}/application")
async def get_audit_application(
    *,
    audit_id: int,
    usecase: GetAdminAuditApplicationUseCase = Depends(get_audit_application_usecase),
) -> AuditApplicationResponse | None:
    """Получить данные заявки."""

    return await usecase.execute(audit_id=audit_id)


@router.get("/{audit_id}/contract")
async def get_audit_contract(
    *,
    audit_id: int,
    usecase: GetAdminAuditContractUseCase = Depends(get_audit_contract_usecase),
) -> AuditContractResponse | None:
    """Получить данные заявки."""

    return await usecase.execute(audit_id=audit_id)
