"""Рассмотрение заявок экспертов."""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse

from src.auth.admin.access import require_admin
from src.auth.admin.dependencies import (
    get_application_certificate_scan_usecase,
    get_approve_expert_application_usecase,
    get_expert_application_usecase,
    get_list_expert_applications_usecase,
    get_reject_expert_application_usecase,
)
from src.auth.admin.schemas.expert_application import (
    ExpertApplicationResponse,
    RejectExpertApplicationRequest,
)
from src.auth.admin.usecases.approve_expert_application import ApproveExpertApplicationUseCase
from src.auth.admin.usecases.get_application_certificate_scan import (
    GetApplicationCertificateScanUseCase,
)
from src.auth.admin.usecases.get_expert_application import GetExpertApplicationUseCase
from src.auth.admin.usecases.list_expert_applications import ListExpertApplicationsUseCase
from src.auth.admin.usecases.reject_expert_application import RejectExpertApplicationUseCase
from src.auth.enums import ApplicationStatus

router = APIRouter(
    prefix="/admin/experts/applications",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)


@router.get("/{application_id}/certificates/{certificate_id}/scan")
async def get_application_certificate_scan(
    *,
    application_id: int,
    certificate_id: int,
    usecase: GetApplicationCertificateScanUseCase = Depends(
        get_application_certificate_scan_usecase
    ),
) -> FileResponse:
    """Получить скан из заявки эксперта."""

    path, filename = await usecase.execute(
        application_id=application_id,
        certificate_id=certificate_id,
    )

    return FileResponse(
        path,
        filename=filename,
    )


@router.get("")
async def list_applications(
    *,
    status_filter: ApplicationStatus | None = Query(
        default=None,
        alias="status",
    ),
    usecase: ListExpertApplicationsUseCase = Depends(get_list_expert_applications_usecase),
) -> list[ExpertApplicationResponse]:
    """Получить заявки экспертов."""

    return await usecase.execute(status=status_filter)


@router.get("/{application_id}")
async def get_application(
    *,
    application_id: int,
    usecase: GetExpertApplicationUseCase = Depends(get_expert_application_usecase),
) -> ExpertApplicationResponse:
    """Открыть заявку эксперта."""

    return await usecase.execute(application_id=application_id)


@router.post("/{application_id}/approve")
async def approve_application(
    *,
    application_id: int,
    usecase: ApproveExpertApplicationUseCase = Depends(get_approve_expert_application_usecase),
) -> ExpertApplicationResponse:
    """Одобрить регистрацию эксперта."""

    return await usecase.execute(application_id=application_id)


@router.post("/{application_id}/reject")
async def reject_application(
    *,
    application_id: int,
    payload: RejectExpertApplicationRequest,
    usecase: RejectExpertApplicationUseCase = Depends(get_reject_expert_application_usecase),
) -> ExpertApplicationResponse:
    """Отклонить заявку эксперта."""

    return await usecase.execute(
        application_id=application_id,
        payload=payload,
    )
