from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.dependencies.users import (
    clear_auth_cookie,
    get_current_user,
    get_login_usecase,
    get_register_usecase,
    set_auth_cookie,
)
from app.models.user import User
from app.schemas.user import LoginSchema, RegisterSchema, UserOutSchema
from app.services.experts.exceptions import ApplicationPendingError
from app.services.security.tokens import create_access_token
from app.services.users.exceptions import (
    EmailAlreadyTakenError,
    InvalidCredentialsError,
    InvalidPhoneError,
    WeakPasswordError,
)
from app.services.users.usecases.login import LoginUserUseCase
from app.services.users.usecases.register import RegisterUserUseCase


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterSchema,
    response: Response,
    usecase: RegisterUserUseCase = Depends(get_register_usecase),
) -> UserOutSchema:
    """Регистрация заказчика. Сразу выдаёт cookie с токеном — отдельно входить не нужно."""

    try:
        user = await usecase.execute(payload)
    except (WeakPasswordError, InvalidPhoneError) as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error
    except EmailAlreadyTakenError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Этот email уже зарегистрирован",
        ) from error

    token = create_access_token(user.id)
    set_auth_cookie(response, token)

    return UserOutSchema.model_validate(user)


@router.post("/login")
async def login(
    payload: LoginSchema,
    response: Response,
    usecase: LoginUserUseCase = Depends(get_login_usecase),
) -> UserOutSchema:
    """Вход по email и паролю. Выдаёт cookie с токеном."""

    try:
        user = await usecase.execute(payload)
    except InvalidCredentialsError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        ) from error
    except ApplicationPendingError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ваша заявка эксперта ещё на рассмотрении. Мы напишем, когда одобрим её.",
        ) from error

    token = create_access_token(user.id)
    set_auth_cookie(response, token)

    return UserOutSchema.model_validate(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response) -> None:
    """Выход: удаляем cookie с токеном."""

    clear_auth_cookie(response)


@router.get("/me")
async def me(user: User = Depends(get_current_user)) -> UserOutSchema:
    """Текущий пользователь по cookie. Фронт вызывает при рендере страницы."""

    return UserOutSchema.model_validate(user)
