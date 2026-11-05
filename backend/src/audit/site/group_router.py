"""Группа аудиторов."""

from fastapi import APIRouter, Depends

from src.audit.schemas.audit import AuditResponse
from src.audit.site.group_dependencies import (
    get_audit_team_usecase,
    get_list_auditors_usecase,
    get_set_audit_team_usecase,
)
from src.audit.site.schemas.audit_plan import (
    AuditTeamMemberResponse,
)
from src.audit.site.schemas.set_audit_team import SetAuditTeamRequest
from src.audit.site.usecases.get_audit_team import GetAuditTeamUseCase
from src.audit.site.usecases.list_auditors import ListAuditorsUseCase
from src.audit.site.usecases.set_audit_team import SetAuditTeamUseCase
from src.auth.site.dependencies import get_current_user, require_expert
from src.users.models.user import User

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
)


@router.get("/auditors")
async def list_auditors(
    *,
    user: User = Depends(require_expert),
    usecase: ListAuditorsUseCase = Depends(get_list_auditors_usecase),
) -> list[AuditTeamMemberResponse]:
    """Получить аудиторов для группы."""

    return await usecase.execute(user=user)


@router.put("/{audit_id}/team")
async def set_audit_team(
    *,
    audit_id: int,
    payload: SetAuditTeamRequest,
    user: User = Depends(require_expert),
    usecase: SetAuditTeamUseCase = Depends(get_set_audit_team_usecase),
) -> AuditResponse:
    """Изменить состав аудиторской группы."""

    return await usecase.execute(
        user=user,
        audit_id=audit_id,
        user_ids=payload.user_ids,
    )


@router.get("/{audit_id}/team")
async def get_audit_team(
    *,
    audit_id: int,
    user: User = Depends(get_current_user),
    usecase: GetAuditTeamUseCase = Depends(get_audit_team_usecase),
) -> list[AuditTeamMemberResponse]:
    """Группа аудиторов."""

    return await usecase.execute(
        audit_id=audit_id,
        user=user,
    )
