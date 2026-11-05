"""Управление обращениями."""

from fastapi import APIRouter, Depends

from src.auth.admin.access import require_admin
from src.requests.admin.dependencies import (
    get_delete_contact_request_usecase,
    get_list_contact_requests_usecase,
)
from src.requests.admin.usecases.delete_contact_request import DeleteContactRequestUseCase
from src.requests.admin.usecases.list_contact_requests import ListContactRequestsUseCase
from src.requests.schemas.contact_request import ContactRequestResponse

router = APIRouter(
    tags=["requests"],
    dependencies=[Depends(require_admin)],
)


@router.get("/requests")
async def list_contact_requests(
    usecase: ListContactRequestsUseCase = Depends(get_list_contact_requests_usecase),
) -> list[ContactRequestResponse]:
    """Получить обращения."""

    return await usecase.execute()


@router.delete(
    "/request/{request_id}",
    status_code=204,
)
async def delete_contact_request(
    request_id: int,
    usecase: DeleteContactRequestUseCase = Depends(get_delete_contact_request_usecase),
) -> None:
    """Удалить обращение."""

    await usecase.execute(request_id=request_id)
