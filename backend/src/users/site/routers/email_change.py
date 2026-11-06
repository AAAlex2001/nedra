"""Смена почты пользователя."""

from fastapi import APIRouter, Depends

from src.auth.site.dependencies.authentication import (
    get_authenticated_user_id,
)
from src.users.site.dependencies.email_change import (
    get_confirm_email_change_usecase,
    get_request_email_change_usecase,
)
from src.users.site.schemas.confirm_email_change import (
    EmailConfirmationRequest,
    EmailConfirmationResponse,
)
from src.users.site.schemas.email_change import (
    EmailChangeRequest,
    EmailCodeSentResponse,
)
from src.users.site.usecases.confirm_email_change import ConfirmEmailChangeUseCase
from src.users.site.usecases.request_email_change import RequestEmailChangeUseCase

router = APIRouter(
    prefix="/auth/me",
    tags=["users"],
)


@router.post("/email")
async def request_email_change(
    *,
    payload: EmailChangeRequest,
    user_id: int = Depends(get_authenticated_user_id),
    usecase: RequestEmailChangeUseCase = Depends(get_request_email_change_usecase),
) -> EmailCodeSentResponse:
    """Отправить код на новый email."""

    return await usecase.execute(
        user_id=user_id,
        email=payload.email,
    )


@router.post("/email/confirm")
async def confirm_email_change(
    *,
    payload: EmailConfirmationRequest,
    user_id: int = Depends(get_authenticated_user_id),
    usecase: ConfirmEmailChangeUseCase = Depends(get_confirm_email_change_usecase),
) -> EmailConfirmationResponse:
    """Подтвердить новый email."""

    return await usecase.execute(
        user_id=user_id,
        code=payload.code,
    )
