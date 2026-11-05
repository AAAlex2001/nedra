"""Подача заявки эксперта."""

from fastapi import APIRouter, Depends

from src.auth.site.expert_application_dependencies import (
    get_submit_expert_application_usecase,
    parse_expert_application_form,
)
from src.auth.site.schemas.expert_application import (
    CreateExpertApplicationRequest,
    ExpertApplicationCreatedResponse,
)
from src.auth.site.usecases.submit_expert_application import SubmitExpertApplicationUseCase

router = APIRouter(
    prefix="/experts/applications",
    tags=["auth"],
)


@router.post(
    "",
    status_code=201,
)
async def submit_application(
    *,
    payload: CreateExpertApplicationRequest = Depends(parse_expert_application_form),
    usecase: SubmitExpertApplicationUseCase = Depends(get_submit_expert_application_usecase),
) -> ExpertApplicationCreatedResponse:
    """Подать заявку на регистрацию эксперта."""

    return await usecase.execute(payload=payload)
