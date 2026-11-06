"""Личный профиль пользователя."""

from fastapi import APIRouter, Depends

from src.auth.site.dependencies.authentication import (
    get_authenticated_user_id,
    get_current_user,
)
from src.users.models.user import User
from src.users.site.dependencies.profile import get_update_profile_usecase
from src.users.site.schemas.update_profile import (
    UpdateProfileRequest,
    UpdateProfileResponse,
)
from src.users.site.schemas.user import UserResponse
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
) -> UpdateProfileResponse:
    """Изменить имя и телефон."""

    return await usecase.execute(
        user_id=user_id,
        payload=payload,
    )
