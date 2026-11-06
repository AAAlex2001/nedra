"""Подробности заявок для администратора."""

from fastapi import APIRouter, Depends

from src.auth.admin.access import require_admin
from src.expertise.admin.dependencies.details import (
    get_expertise_contract_usecase,
    get_expertise_participants_usecase,
    get_expertise_usecase,
)
from src.expertise.admin.usecases.get_expertise import GetAdminExpertiseUseCase
from src.expertise.admin.usecases.get_expertise_contract import (
    GetAdminExpertiseContractUseCase,
)
from src.expertise.admin.usecases.get_expertise_participants import (
    GetAdminExpertiseParticipantsUseCase,
)
from src.expertise.schemas.expertise import ExpertiseResponse
from src.expertise.schemas.expertise_contract import ExpertiseContractResponse
from src.expertise.schemas.expertise_participants import ExpertiseParticipantsResponse

router = APIRouter(
    prefix="/admin/expertises",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)


@router.get("/{expertise_id}")
async def get_expertise(
    *,
    expertise_id: int,
    usecase: GetAdminExpertiseUseCase = Depends(get_expertise_usecase),
) -> ExpertiseResponse:
    """Получить данные заявки."""

    return await usecase.execute(expertise_id=expertise_id)


@router.get("/{expertise_id}/participants")
async def get_expertise_participants(
    *,
    expertise_id: int,
    usecase: GetAdminExpertiseParticipantsUseCase = Depends(get_expertise_participants_usecase),
) -> ExpertiseParticipantsResponse:
    """Получить данные заявки."""

    return await usecase.execute(expertise_id=expertise_id)


@router.get("/{expertise_id}/contract")
async def get_expertise_contract(
    *,
    expertise_id: int,
    usecase: GetAdminExpertiseContractUseCase = Depends(get_expertise_contract_usecase),
) -> ExpertiseContractResponse | None:
    """Получить данные заявки."""

    return await usecase.execute(expertise_id=expertise_id)
