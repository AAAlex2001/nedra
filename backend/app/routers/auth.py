from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, status

from app.dependencies.users import (
    clear_auth_cookie,
    get_confirm_email_change_usecase,
    get_current_user,
    get_login_usecase,
    get_register_usecase,
    get_request_email_change_usecase,
    get_update_profile_usecase,
    set_auth_cookie,
)
from app.models.user import User
from app.schemas.user import (
    EmailChangeSchema,
    EmailCodeSentSchema,
    EmailConfirmSchema,
    LoginSchema,
    ProfileUpdateSchema,
    RegisterSchema,
    UserOutSchema,
)
from app.services.experts.exceptions import ApplicationPendingError
from app.services.security.tokens import create_access_token
from app.services.users.exceptions import (
    EmailAlreadyTakenError,
    EmailChangeError,
    EmailCodeCooldownError,
    InvalidCredentialsError,
    InvalidPhoneError,
    WeakPasswordError,
)
from app.services.users.letters import send_email_change_code
from app.services.users.usecases.change_email import (
    ConfirmEmailChangeUseCase,
    RequestEmailChangeUseCase,
)
from app.services.users.usecases.login import LoginUserUseCase
from app.services.users.usecases.register import RegisterUserUseCase
from app.services.users.usecases.update_profile import UpdateProfileUseCase


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


@router.patch("/me")
async def update_me(
    payload: ProfileUpdateSchema,
    user: User = Depends(get_current_user),
    usecase: UpdateProfileUseCase = Depends(get_update_profile_usecase),
) -> UserOutSchema:
    """Сменить имя и телефон."""

    try:
        updated = await usecase.execute(user, payload.full_name, payload.phone)
    except InvalidPhoneError as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(error)) from error

    return UserOutSchema.model_validate(updated)


@router.post("/me/email")
async def request_email_change(
    payload: EmailChangeSchema,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    usecase: RequestEmailChangeUseCase = Depends(get_request_email_change_usecase),
) -> EmailCodeSentSchema:
    """Отправить код подтверждения на новый email. Пока прежний код действует, новый не шлём."""

    try:
        sent = await usecase.execute(user, payload.email)
    except EmailChangeError as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(error)) from error
    except EmailAlreadyTakenError as error:
        raise HTTPException(status.HTTP_409_CONFLICT, "Этот email уже занят") from error
    except EmailCodeCooldownError as error:
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS,
            str(error),
            headers={"Retry-After": str(error.seconds)},
        ) from error

    if sent.code is not None:
        background_tasks.add_task(send_email_change_code, sent.email, user.full_name, sent.code)

    return EmailCodeSentSchema(email=sent.email, resend_in=sent.resend_in)


@router.post("/me/email/confirm")
async def confirm_email_change(
    payload: EmailConfirmSchema,
    user: User = Depends(get_current_user),
    usecase: ConfirmEmailChangeUseCase = Depends(get_confirm_email_change_usecase),
) -> UserOutSchema:
    """Подтвердить новый email кодом из письма."""

    try:
        updated = await usecase.execute(user, payload.code)
    except EmailChangeError as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(error)) from error
    except EmailAlreadyTakenError as error:
        raise HTTPException(status.HTTP_409_CONFLICT, "Этот email уже занят") from error

    return UserOutSchema.model_validate(updated)
