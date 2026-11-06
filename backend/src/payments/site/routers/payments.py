"""Оплата пользователя и уведомления провайдера."""

from fastapi import APIRouter, Depends

from src.auth.site.dependencies.authentication import get_current_user
from src.payments.schemas.payment import PaymentResponse
from src.payments.site.dependencies.payments import (
    get_create_payment_usecase,
    get_payment_usecase,
    get_refresh_payment_usecase,
)
from src.payments.site.schemas.create_payment import (
    CreatePaymentRequest,
    CreatePaymentResponse,
)
from src.payments.site.usecases.create_payment import CreatePaymentUseCase
from src.payments.site.usecases.get_payment import GetPaymentUseCase
from src.payments.site.usecases.refresh_payment import RefreshPaymentUseCase
from src.users.models.user import User

router = APIRouter(
    prefix="/payments",
    tags=["payments"],
)


@router.post("", status_code=201)
async def create_payment(
    *,
    payload: CreatePaymentRequest,
    user: User = Depends(get_current_user),
    usecase: CreatePaymentUseCase = Depends(get_create_payment_usecase),
) -> CreatePaymentResponse:
    """Создать платёж пользователя."""

    return await usecase.execute(
        user=user,
        payload=payload,
    )


@router.get("/{payment_id}")
async def get_payment(
    *,
    payment_id: int,
    user: User = Depends(get_current_user),
    usecase: GetPaymentUseCase = Depends(get_payment_usecase),
) -> PaymentResponse:
    """Открыть свой платёж."""

    return await usecase.execute(
        payment_id=payment_id,
        user_id=user.id,
    )


@router.post("/{payment_id}/refresh")
async def refresh_payment(
    *,
    payment_id: int,
    user: User = Depends(get_current_user),
    usecase: RefreshPaymentUseCase = Depends(get_refresh_payment_usecase),
) -> PaymentResponse:
    """Проверить статус оплаты."""

    return await usecase.execute(
        payment_id=payment_id,
        user_id=user.id,
    )
