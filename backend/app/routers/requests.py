from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from app.dependencies.admin import require_admin
from app.dependencies.requests import get_create_request_usecase, get_request_repository
from app.schemas.request import RequestInSchema, RequestOutSchema
from app.services.requests.exceptions import UnknownActivityError
from app.services.requests.letter import send_new_request_letter
from app.services.requests.repo import RequestRepository
from app.services.requests.usecases.create_request import CreateRequestUseCase


router = APIRouter(tags=["requests"])


@router.post("/request", status_code=status.HTTP_201_CREATED)
async def create_request(
    payload: RequestInSchema,
    background_tasks: BackgroundTasks,
    usecase: CreateRequestUseCase = Depends(get_create_request_usecase),
) -> RequestOutSchema:
    """Создание заявки. Письмо менеджерам уходит в фоне, после ответа клиенту."""

    try:
        request = await usecase.execute(payload)
    except UnknownActivityError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error

    background_tasks.add_task(send_new_request_letter, request)

    return RequestOutSchema.model_validate(request)


@router.get("/requests", dependencies=[Depends(require_admin)])
async def get_all_requests(
    requests: RequestRepository = Depends(get_request_repository),
) -> list[RequestOutSchema]:
    """Все заявки для админки."""

    items = await requests.list_all()

    return [RequestOutSchema.model_validate(item) for item in items]


@router.delete(
    "/request/{request_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
async def delete_request(
    request_id: int,
    requests: RequestRepository = Depends(get_request_repository),
) -> None:
    """Удаление заявки."""

    request = await requests.get_by_id(request_id)
    if request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Заявка с ID {request_id} не найдена",
        )

    await requests.delete(request)
