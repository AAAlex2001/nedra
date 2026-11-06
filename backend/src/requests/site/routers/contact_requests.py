"""Подача обращения с сайта."""

from fastapi import APIRouter, Depends

from src.requests.schemas.contact_request import (
    ContactRequestResponse,
    CreateContactRequest,
)
from src.requests.site.dependencies.contact_requests import (
    get_create_contact_request_usecase,
)
from src.requests.site.usecases.create_contact_request import (
    CreateContactRequestUseCase,
)

router = APIRouter(tags=["requests"])


@router.post(
    "/request",
    status_code=201,
)
async def create_contact_request(
    payload: CreateContactRequest,
    usecase: CreateContactRequestUseCase = Depends(get_create_contact_request_usecase),
) -> ContactRequestResponse:
    """Подать обращение."""

    return await usecase.execute(payload=payload)
