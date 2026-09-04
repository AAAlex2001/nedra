from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_request_service
from app.models.request import Request
from app.schemas.request import RequestInSchema, RequestOutSchema
from app.services.request import RequestService


router = APIRouter(tags=["requests"])


@router.post(
    "/request",
    response_model=RequestOutSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_request(
    payload: RequestInSchema,
    service: RequestService = Depends(get_request_service),
) -> Request:
    """Создание заявки."""

    try:
        return await service.create_request(payload)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error


@router.get(
    "/requests",
    response_model=list[RequestOutSchema],
    status_code=status.HTTP_200_OK,
)
async def get_all_requests(
    service: RequestService = Depends(get_request_service),
) -> list[Request]:
    """Получение всех заявок."""

    return await service.get_all_requests()