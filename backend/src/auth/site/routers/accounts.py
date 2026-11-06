"""Регистрация, вход и выход."""

from fastapi import APIRouter, Depends, Response

from src.auth.site.cookies import clear_auth_cookie, set_auth_cookie
from src.auth.site.dependencies.accounts import get_login_usecase, get_register_usecase
from src.auth.site.schemas.login import LoginRequest, LoginResponse
from src.auth.site.schemas.register import RegisterRequest, RegisterResponse
from src.auth.site.usecases.login import LoginUserUseCase
from src.auth.site.usecases.register import RegisterUserUseCase
from src.auth.tokens import create_access_token
from src.core.settings import Settings, get_settings

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post(
    "/register",
    status_code=201,
)
async def register(
    *,
    payload: RegisterRequest,
    response: Response,
    usecase: RegisterUserUseCase = Depends(get_register_usecase),
    settings: Settings = Depends(get_settings),
) -> RegisterResponse:
    """Зарегистрировать заказчика."""

    user = await usecase.execute(payload=payload)
    token = create_access_token(
        user_id=user.id,
        settings=settings,
    )
    set_auth_cookie(
        response=response,
        token=token,
        settings=settings,
    )

    return user


@router.post("/login")
async def login(
    *,
    payload: LoginRequest,
    response: Response,
    usecase: LoginUserUseCase = Depends(get_login_usecase),
    settings: Settings = Depends(get_settings),
) -> LoginResponse:
    """Войти в личный кабинет."""

    user = await usecase.execute(payload=payload)
    token = create_access_token(
        user_id=user.id,
        settings=settings,
    )
    set_auth_cookie(
        response=response,
        token=token,
        settings=settings,
    )

    return user


@router.post(
    "/logout",
    status_code=204,
)
async def logout(
    *,
    response: Response,
    settings: Settings = Depends(get_settings),
) -> None:
    """Выйти из аккаунта."""

    clear_auth_cookie(
        response=response,
        settings=settings,
    )
