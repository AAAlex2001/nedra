"""Согласование плана."""

from fastapi import APIRouter, Depends

from src.audit.schemas.audit import AuditResponse
from src.audit.site.dependencies.plans import (
    get_approve_audit_plan_usecase,
    get_audit_plan_usecase,
    get_request_audit_plan_changes_usecase,
    get_submit_audit_plan_usecase,
)
from src.audit.site.schemas.audit_plan import AuditPlanReviewResponse
from src.audit.site.schemas.request_audit_plan_changes import (
    RequestAuditPlanChangesRequest,
    RequestAuditPlanChangesResponse,
)
from src.audit.site.schemas.submit_audit_plan import (
    SubmitAuditPlanRequest,
    SubmitAuditPlanResponse,
)
from src.audit.site.usecases.approve_audit_plan import ApproveAuditPlanUseCase
from src.audit.site.usecases.get_audit_plan import GetAuditPlanUseCase
from src.audit.site.usecases.request_audit_plan_changes import (
    RequestAuditPlanChangesUseCase,
)
from src.audit.site.usecases.submit_audit_plan import SubmitAuditPlanUseCase
from src.auth.site.dependencies.authentication import (
    get_current_user,
    require_customer,
    require_expert,
)
from src.users.models.user import User

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
)


@router.post("/{audit_id}/plan")
async def submit_audit_plan(
    *,
    audit_id: int,
    payload: SubmitAuditPlanRequest,
    user: User = Depends(require_expert),
    usecase: SubmitAuditPlanUseCase = Depends(get_submit_audit_plan_usecase),
) -> SubmitAuditPlanResponse:
    """Отправить план аудита заказчику."""

    return await usecase.execute(
        user=user,
        audit_id=audit_id,
        payload=payload,
    )


@router.post("/{audit_id}/plan/approve")
async def approve_audit_plan(
    *,
    audit_id: int,
    user: User = Depends(require_customer),
    usecase: ApproveAuditPlanUseCase = Depends(get_approve_audit_plan_usecase),
) -> AuditResponse:
    """Согласовать план аудита."""

    return await usecase.execute(
        user=user,
        audit_id=audit_id,
    )


@router.post("/{audit_id}/plan/changes")
async def request_audit_plan_changes(
    *,
    audit_id: int,
    payload: RequestAuditPlanChangesRequest,
    user: User = Depends(require_customer),
    usecase: RequestAuditPlanChangesUseCase = Depends(get_request_audit_plan_changes_usecase),
) -> RequestAuditPlanChangesResponse:
    """Запросить изменения плана аудита."""

    return await usecase.execute(
        user=user,
        audit_id=audit_id,
        comment=payload.comment,
    )


@router.get("/{audit_id}/plan")
async def get_audit_plan(
    *,
    audit_id: int,
    user: User = Depends(get_current_user),
    usecase: GetAuditPlanUseCase = Depends(get_audit_plan_usecase),
) -> AuditPlanReviewResponse | None:
    """План и согласование."""

    return await usecase.execute(
        audit_id=audit_id,
        user=user,
    )
