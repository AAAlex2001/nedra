"""Подача заявки кандидата с сайта."""

from fastapi import APIRouter, Depends

from src.commission.schemas.commission_application import (
    CommissionApplicationResponse,
    CreateCommissionApplicationRequest,
)
from src.commission.site.dependencies import get_create_commission_application_usecase
from src.commission.site.usecases.create_commission_application import (
    CreateCommissionApplicationUseCase,
)

router = APIRouter(
    prefix="/commission",
    tags=["commission"],
)


@router.post(
    "/applications",
    status_code=201,
)
async def create_commission_application(
    payload: CreateCommissionApplicationRequest,
    usecase: CreateCommissionApplicationUseCase = Depends(
        get_create_commission_application_usecase
    ),
) -> CommissionApplicationResponse:
    """Подать заявку кандидата."""

    return await usecase.execute(payload=payload)
