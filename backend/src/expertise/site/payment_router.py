"""Оплата экспертизы картой."""

from fastapi import APIRouter, Depends

from src.auth.site.dependencies import require_customer
from src.expertise.site.payment_dependencies import get_create_expertise_payment_usecase
from src.expertise.site.usecases.create_payment import CreateExpertisePaymentUseCase
from src.payments.schemas.payment import PaymentResponse
from src.users.models.user import User

router = APIRouter(
    prefix="/expertises",
    tags=["expertise"],
)


@router.post("/{expertise_id}/payment")
async def create_payment(
    *,
    expertise_id: int,
    user: User = Depends(require_customer),
    usecase: CreateExpertisePaymentUseCase = Depends(get_create_expertise_payment_usecase),
) -> PaymentResponse:
    """Получить ссылку на оплату."""

    return await usecase.execute(
        expertise_id=expertise_id,
        user=user,
    )
