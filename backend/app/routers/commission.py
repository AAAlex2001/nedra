from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from app.dependencies.admin import require_admin
from app.dependencies.commission import (
    get_commission_repository,
    get_create_commission_application_usecase,
)
from app.schemas.commission import CommissionApplicationInSchema, CommissionApplicationOutSchema
from app.services.commission.letter import send_commission_letter
from app.services.commission.repo import CommissionRepository
from app.services.commission.usecases.create_application import (
    CreateCommissionApplicationUseCase,
)
from app.services.experts.exceptions import InvalidCertificateError


router = APIRouter(tags=["commission"])


@router.post("/commission/applications", status_code=status.HTTP_201_CREATED)
async def create_commission_application(
    payload: CommissionApplicationInSchema,
    background_tasks: BackgroundTasks,
    usecase: CreateCommissionApplicationUseCase = Depends(get_create_commission_application_usecase),
) -> CommissionApplicationOutSchema:
    """Заявка кандидата в конкурсную комиссию. Письмо менеджерам уходит в фоне."""

    try:
        application = await usecase.execute(payload)
    except InvalidCertificateError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error

    background_tasks.add_task(send_commission_letter, application)

    return CommissionApplicationOutSchema.model_validate(application)


@router.get("/admin/commission/applications", dependencies=[Depends(require_admin)])
async def list_commission_applications(
    applications: CommissionRepository = Depends(get_commission_repository),
) -> list[CommissionApplicationOutSchema]:
    """Все заявки кандидатов для админки."""

    items = await applications.list_all()

    return [CommissionApplicationOutSchema.model_validate(item) for item in items]


@router.delete(
    "/admin/commission/applications/{application_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
async def delete_commission_application(
    application_id: int,
    applications: CommissionRepository = Depends(get_commission_repository),
) -> None:
    """Удаление заявки кандидата."""

    application = await applications.get_by_id(application_id)
    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Заявка с ID {application_id} не найдена",
        )

    await applications.delete(application)
