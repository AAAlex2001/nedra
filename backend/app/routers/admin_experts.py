from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse

from app.dependencies.admin import require_admin
from app.dependencies.experts import (
    get_application_repository,
    get_approve_application_usecase,
    get_delete_expert_usecase,
    get_private_storage,
    get_reject_application_usecase,
)
from app.models.expert import ApplicationStatus, ExpertApplication
from app.schemas.expert import ExpertApplicationOutSchema, RejectApplicationSchema
from app.services.experts.exceptions import (
    ApplicationAlreadyReviewedError,
    ApplicationNotFoundError,
    ExpertNotFoundError,
)
from app.services.experts.letters import send_application_approved, send_application_rejected
from app.services.experts.repo import ExpertApplicationRepository
from app.services.experts.usecases.approve_application import ApproveExpertApplicationUseCase
from app.services.experts.usecases.delete_expert import DeleteExpertUseCase
from app.services.experts.usecases.reject_application import RejectExpertApplicationUseCase
from app.services.files.storage import PrivateStorage
from app.services.users.exceptions import EmailAlreadyTakenError


router = APIRouter(
    prefix="/admin/experts",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)


async def get_application_or_404(
    application_id: int,
    applications: ExpertApplicationRepository = Depends(get_application_repository),
) -> ExpertApplication:
    """Заявка из пути /applications/{application_id}. Нет — 404."""

    application = await applications.get_by_id(application_id)
    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Заявка {application_id} не найдена",
        )

    return application


@router.get("/applications")
async def list_applications(
    status_filter: ApplicationStatus | None = Query(None, alias="status"),
    applications: ExpertApplicationRepository = Depends(get_application_repository),
) -> list[ExpertApplicationOutSchema]:
    """Заявки экспертов, новые первыми. По умолчанию все, можно отфильтровать по статусу."""

    items = await applications.list_all(status_filter)

    return [ExpertApplicationOutSchema.model_validate(item) for item in items]


@router.get("/applications/{application_id}")
async def get_application(
    application: ExpertApplication = Depends(get_application_or_404),
) -> ExpertApplicationOutSchema:
    """Одна заявка со всеми удостоверениями."""

    return ExpertApplicationOutSchema.model_validate(application)


@router.post("/applications/{application_id}/approve")
async def approve_application(
    application_id: int,
    background_tasks: BackgroundTasks,
    usecase: ApproveExpertApplicationUseCase = Depends(get_approve_application_usecase),
) -> ExpertApplicationOutSchema:
    """Одобрить заявку: создаётся пользователь-эксперт, ему уходит письмо."""

    try:
        application = await usecase.execute(application_id)
    except ApplicationNotFoundError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(error)) from error
    except ApplicationAlreadyReviewedError as error:
        raise HTTPException(status.HTTP_409_CONFLICT, str(error)) from error
    except EmailAlreadyTakenError as error:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Пользователь с таким email уже есть, одобрить нельзя",
        ) from error

    background_tasks.add_task(send_application_approved, application)

    return ExpertApplicationOutSchema.model_validate(application)


@router.post("/applications/{application_id}/reject")
async def reject_application(
    application_id: int,
    payload: RejectApplicationSchema,
    background_tasks: BackgroundTasks,
    usecase: RejectExpertApplicationUseCase = Depends(get_reject_application_usecase),
) -> ExpertApplicationOutSchema:
    """Отклонить заявку с причиной, эксперту уходит письмо."""

    try:
        application = await usecase.execute(application_id, payload.comment)
    except ApplicationNotFoundError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(error)) from error
    except ApplicationAlreadyReviewedError as error:
        raise HTTPException(status.HTTP_409_CONFLICT, str(error)) from error

    background_tasks.add_task(send_application_rejected, application)

    return ExpertApplicationOutSchema.model_validate(application)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expert(
    user_id: int,
    usecase: DeleteExpertUseCase = Depends(get_delete_expert_usecase),
) -> None:
    """Удалить аккаунт эксперта. Его заявка остаётся в истории как отклонённая."""

    try:
        await usecase.execute(user_id)
    except ExpertNotFoundError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(error)) from error


@router.get("/applications/{application_id}/certificates/{certificate_id}/scan")
async def download_certificate_scan(
    certificate_id: int,
    application: ExpertApplication = Depends(get_application_or_404),
    storage: PrivateStorage = Depends(get_private_storage),
) -> FileResponse:
    """Скан удостоверения из закрытого хранилища."""

    certificate = None
    for item in application.certificates:
        if item.id == certificate_id:
            certificate = item

    if certificate is None or certificate.scan_path is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Скан не найден",
        )

    try:
        path = storage.resolve(certificate.scan_path)
    except FileNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Файл скана отсутствует на диске",
        ) from error

    return FileResponse(path, filename=certificate.scan_name or path.name)
