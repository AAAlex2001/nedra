from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from app.dependencies import get_request_service
from app.schemas.request import RequestInSchema, RequestOutSchema
from app.services.email import send_new_request
from app.services.request import RequestService


router = APIRouter(tags=["requests"])


@router.post("/request", status_code=status.HTTP_201_CREATED)
async def create_request(
    payload: RequestInSchema,
    background_tasks: BackgroundTasks,
    service: RequestService = Depends(get_request_service),
) -> RequestOutSchema:
    """Создание заявки."""

    try:
        request = await service.create_request(payload)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error

    created = RequestOutSchema.model_validate(request)
    background_tasks.add_task(send_new_request, created)

    return created


@router.get("/requests")
async def get_all_requests(
    service: RequestService = Depends(get_request_service),
) -> list[RequestOutSchema]:
    """Получение всех заявок."""

    requests = await service.get_all_requests()

    return [RequestOutSchema.model_validate(request) for request in requests]

@router.delete("/request/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_request(
    request_id: int,
    service: RequestService = Depends(get_request_service),
) -> None:
    """Удаление заявки."""

    try:
        await service.delete_request(request_id)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
