"""Личный профиль пользователя."""

from fastapi import APIRouter, Depends

from src.auth.site.dependencies import get_authenticated_user_id, get_current_user
from src.users.models.user import User
from src.users.site.dependencies import (
    get_confirm_email_change_usecase,
    get_request_email_change_usecase,
    get_update_profile_usecase,
)
from src.users.site.schemas.email_change import (
    EmailChangeRequest,
    EmailCodeSentResponse,
    EmailConfirmationRequest,
)
from src.users.site.schemas.update_profile import UpdateProfileRequest
from src.users.site.schemas.user import UserResponse
from src.users.site.usecases.confirm_email_change import ConfirmEmailChangeUseCase
from src.users.site.usecases.request_email_change import RequestEmailChangeUseCase
from src.users.site.usecases.update_profile import UpdateProfileUseCase

router = APIRouter(
    prefix="/auth/me",
    tags=["users"],
)


@router.get("")
async def get_profile(*, user: User = Depends(get_current_user)) -> UserResponse:
    """Получить свой профиль."""

    return UserResponse.from_model(user=user)


@router.patch("")
async def update_profile(
    *,
    payload: UpdateProfileRequest,
    user_id: int = Depends(get_authenticated_user_id),
    usecase: UpdateProfileUseCase = Depends(get_update_profile_usecase),
) -> UserResponse:
    """Изменить имя и телефон."""

    return await usecase.execute(
        user_id=user_id,
        payload=payload,
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
) -> UserResponse:
    """Подтвердить новый email."""

    return await usecase.execute(
        user_id=user_id,
        code=payload.code,
    )
