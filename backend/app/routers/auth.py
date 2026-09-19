from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.dependencies.experts import get_profile_repository
from app.dependencies.users import (
    clear_auth_cookie,
    get_current_user,
    get_login_usecase,
    get_register_usecase,
    get_switch_role_usecase,
    set_auth_cookie,
)
from app.models.user import User
from app.schemas.user import LoginSchema, RegisterSchema, RoleSwitchSchema, UserOutSchema
from app.services.experts.exceptions import ApplicationPendingError
from app.services.experts.repo import ExpertProfileRepository
from app.services.security.tokens import create_access_token
from app.services.users.exceptions import (
    EmailAlreadyTakenError,
    InvalidCredentialsError,
    InvalidPhoneError,
    RoleNotAvailableError,
    WeakPasswordError,
)
from app.services.users.usecases.login import LoginUserUseCase
from app.services.users.usecases.register import RegisterUserUseCase
from app.services.users.usecases.switch_role import SwitchRoleUseCase


router = APIRouter(prefix="/auth", tags=["auth"])


async def to_user_schema(user: User, profiles: ExpertProfileRepository) -> UserOutSchema:
    """Собрать ответ с признаком, есть ли у аккаунта профиль эксперта."""

    profile = await profiles.get_by_user(user.id)

    return UserOutSchema(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        role=user.role,
        is_expert=profile is not None,
        created_at=user.created_at,
    )


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterSchema,
    response: Response,
    usecase: RegisterUserUseCase = Depends(get_register_usecase),
    profiles: ExpertProfileRepository = Depends(get_profile_repository),
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
            detail="Этот email уже зарегистрирован. Войдите: роли переключаются в кабинете",
        ) from error

    token = create_access_token(user.id)
    set_auth_cookie(response, token)

    return await to_user_schema(user, profiles)


@router.post("/login")
async def login(
    payload: LoginSchema,
    response: Response,
    usecase: LoginUserUseCase = Depends(get_login_usecase),
    profiles: ExpertProfileRepository = Depends(get_profile_repository),
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

    return await to_user_schema(user, profiles)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response) -> None:
    """Выход: удаляем cookie с токеном."""

    clear_auth_cookie(response)


@router.get("/me")
async def me(
    user: User = Depends(get_current_user),
    profiles: ExpertProfileRepository = Depends(get_profile_repository),
) -> UserOutSchema:
    """Текущий пользователь по cookie. Фронт вызывает при рендере страницы."""

    return await to_user_schema(user, profiles)


@router.post("/role")
async def switch_role(
    payload: RoleSwitchSchema,
    user: User = Depends(get_current_user),
    usecase: SwitchRoleUseCase = Depends(get_switch_role_usecase),
    profiles: ExpertProfileRepository = Depends(get_profile_repository),
) -> UserOutSchema:
    """Переключить активную роль: заказчик или эксперт."""

    try:
        updated = await usecase.execute(user, payload.role)
    except RoleNotAvailableError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        ) from error

    return await to_user_schema(updated, profiles)
