"""Управление работами администратором."""

from fastapi import APIRouter, Depends

from src.audit.admin.dependencies.audits import (
    get_delete_audit_usecase,
    get_list_audits_usecase,
    get_update_audit_usecase,
)
from src.audit.admin.schemas.audit import AuditAdminResponse, UpdateAuditRequest
from src.audit.admin.usecases.delete_audit import DeleteAuditUseCase
from src.audit.admin.usecases.list_audits import ListAdminAuditsUseCase
from src.audit.admin.usecases.update_audit import UpdateAuditUseCase
from src.auth.admin.access import require_admin

router = APIRouter(
    prefix="/admin/audits",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)


@router.get("")
async def list_audits(
    *, usecase: ListAdminAuditsUseCase = Depends(get_list_audits_usecase)
) -> list[AuditAdminResponse]:
    """Получить все работы."""

    return await usecase.execute()


@router.patch("/{audit_id}", status_code=204)
async def update_audit(
    *,
    audit_id: int,
    payload: UpdateAuditRequest,
    usecase: UpdateAuditUseCase = Depends(get_update_audit_usecase),
) -> None:
    """Изменить работу."""

    await usecase.execute(
        audit_id=audit_id,
        payload=payload,
    )


@router.delete("/{audit_id}", status_code=204)
async def delete_audit(
    *,
    audit_id: int,
    usecase: DeleteAuditUseCase = Depends(get_delete_audit_usecase),
) -> None:
    """Удалить работу."""

    await usecase.execute(audit_id=audit_id)
