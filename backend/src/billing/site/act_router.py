"""Акты выполненных работ."""

from fastapi import APIRouter, Depends

from src.auth.site.dependencies import require_customer
from src.billing.schemas.act import ActResponse
from src.billing.site.dependencies import get_list_acts_usecase
from src.billing.site.usecases.list_acts import ListActsUseCase
from src.users.models.user import User

router = APIRouter(
    prefix="/acts",
    tags=["billing"],
)


@router.get("")
async def list_acts(
    *,
    user: User = Depends(require_customer),
    usecase: ListActsUseCase = Depends(get_list_acts_usecase),
) -> list[ActResponse]:
    """Получить свои акты."""

    return await usecase.execute(user_id=user.id)
