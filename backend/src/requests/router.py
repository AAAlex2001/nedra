"""HTTP-маршруты заявок."""

from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, status

from src.core.admin import require_admin
from src.requests.dependencies import (
    get_create_request_use_case,
    get_delete_request_use_case,
    get_list_requests_use_case,
)
from src.requests.letters import send_new_request_letter
from src.requests.schemas import RequestInSchema, RequestOutSchema
from src.requests.use_cases import (
    CreateRequestUseCase,
    DeleteRequestUseCase,
    ListRequestsUseCase,
)

router = APIRouter(tags=["requests"])


@router.post("/request", response_model=RequestOutSchema, status_code=status.HTTP_201_CREATED)
async def create_request(
    *,
    data: RequestInSchema,
    background_tasks: BackgroundTasks,
    use_case: Annotated[CreateRequestUseCase, Depends(get_create_request_use_case)],
) -> RequestOutSchema:
    """Создаёт новую заявку и уведомляет менеджеров."""

    request = await use_case.execute(data=data)
    background_tasks.add_task(send_new_request_letter, request=request)
    return RequestOutSchema.from_model(model=request)


@router.get(
    "/requests",
    response_model=list[RequestOutSchema],
    dependencies=[Depends(require_admin)],
)
async def list_requests(
    *,
    use_case: Annotated[ListRequestsUseCase, Depends(get_list_requests_use_case)],
) -> list[RequestOutSchema]:
    """Возвращает все заявки для админки."""

    requests = await use_case.execute()
    return [RequestOutSchema.from_model(model=item) for item in requests]


@router.delete(
    "/request/{request_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
async def delete_request(
    *,
    request_id: int,
    use_case: Annotated[DeleteRequestUseCase, Depends(get_delete_request_use_case)],
) -> None:
    """Удаляет заявку по идентификатору."""

    await use_case.execute(request_id=request_id)
