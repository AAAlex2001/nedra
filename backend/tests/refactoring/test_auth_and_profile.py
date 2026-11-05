"""Регистрация, вход и изменение контактов."""

import asyncio
import os
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import jwt
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.auth.enums import ApplicationStatus
from src.auth.models.expert_application import ExpertApplication
from src.auth.options import AUTH_COOKIE, JWT_ALGORITHM
from src.auth.passwords import hash_password
from src.auth.tokens import create_access_token, read_user_id
from src.core.settings import Settings
from src.main import create_app
from src.users.exceptions import EmailChangeError, EmailCodeCooldownError, EmailCodeDeliveryError
from src.users.models.email_change import EmailChange
from src.users.models.user import User
from src.users.site.dependencies import (
    get_confirm_email_change_usecase,
    get_request_email_change_usecase,
)


async def test_registration_login_profile_and_logout(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
) -> None:
    """Пройти регистрацию, изменение профиля и повторный вход."""

    app = create_app(settings=settings)
    app.state.session_factory = session_factory
    payload = {
        "email": "Customer@Example.com",
        "password": "Password123",
        "full_name": "  Иван Иванов  ",
        "phone": "+7 (999) 000-00-01",
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        response = await client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 201
        assert response.json()["email"] == "customer@example.com"
        assert response.json()["full_name"] == "Иван Иванов"
        assert response.json()["phone"] == "+79990000001"
        assert response.json()["role"] == "customer"
        assert "password" not in response.text
        assert "HttpOnly" in response.headers["set-cookie"]
        assert "Secure" in response.headers["set-cookie"]

        response = await client.patch(
            "/api/v1/auth/me",
            json={"full_name": "Пётр Петров", "phone": "+79990000002"},
        )
        assert response.status_code == 200
        assert response.json()["full_name"] == "Пётр Петров"
        assert (await client.get("/api/v1/auth/me")).json()["full_name"] == "Пётр Петров"
        assert (await client.post("/api/v1/auth/logout")).status_code == 204
        assert (await client.get("/api/v1/auth/me")).status_code == 401

        response = await client.post(
            "/api/v1/auth/login",
            json={"email": payload["email"], "password": payload["password"]},
        )
        assert response.status_code == 200
        assert (await client.get("/api/v1/auth/me")).status_code == 200


@pytest.mark.parametrize("password", ["x7Q", "а" * 36 + "1", "a" * 80])
async def test_invalid_password_is_not_saved_or_echoed(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    password: str,
) -> None:
    """Отклонить слабый или слишком длинный пароль."""

    app = create_app(settings=settings)
    app.state.session_factory = session_factory
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": password,
                "full_name": "Иван Иванов",
                "phone": "+79990000001",
            },
        )
        assert response.status_code == 422
        assert password not in response.text

    async with session_factory() as session:
        assert await session.scalar(select(func.count()).select_from(User)) == 0


async def test_pending_expert_must_prove_password(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
) -> None:
    """Показывать статус заявки только после проверки пароля."""

    async with session_factory() as session:
        session.add(
            ExpertApplication(
                email="expert@example.com",
                password_hash=hash_password(password="Password123"),
                full_name="Эксперт",
                phone="+79990000001",
                status=ApplicationStatus.PENDING,
            )
        )
        await session.commit()

    app = create_app(settings=settings)
    app.state.session_factory = session_factory
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "expert@example.com", "password": "Wrong123"},
        )
        assert response.status_code == 401
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "expert@example.com", "password": "Password123"},
        )
        assert response.status_code == 403
        assert AUTH_COOKIE not in client.cookies


@pytest.mark.parametrize("subject", ["not-an-id", "-1", "0", "2147483648", "١", "1.2", None])
def test_invalid_token_subject(*, settings: Settings, subject: object) -> None:
    """Отклонить неподходящий номер пользователя."""

    token = jwt.encode(
        {"sub": subject, "exp": datetime.now(UTC) + timedelta(minutes=1)},
        settings.jwt_secret,
        algorithm=JWT_ALGORITHM,
    )
    assert read_user_id(token=token, settings=settings) is None


@pytest.mark.parametrize("expiration", [None, "invalid", float("inf"), 1])
def test_invalid_token_expiration(*, settings: Settings, expiration: object) -> None:
    """Отклонить повреждённый или просроченный токен."""

    token = jwt.encode(
        {"sub": "1", "exp": expiration}, settings.jwt_secret, algorithm=JWT_ALGORITHM
    )
    assert read_user_id(token=token, settings=settings) is None


async def test_email_change_updates_user_and_application(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    audit_ids: tuple[int, int, int],
) -> None:
    """Изменить почту аккаунта и заявки одним подтверждением."""

    _, _, user_id = audit_ids
    async with session_factory() as session:
        session.add(
            ExpertApplication(
                email="lead@example.com",
                password_hash="unused",
                full_name="Эксперт",
                phone="+79990000002",
                status=ApplicationStatus.APPROVED,
                user_id=user_id,
            )
        )
        await session.commit()

    async with session_factory() as session:
        usecase = get_request_email_change_usecase(session=session, settings=settings)
        usecase.letters.send_email_code = AsyncMock(return_value=True)
        result = await usecase.execute(user_id=user_id, email="New@Example.com")
        code = usecase.letters.send_email_code.call_args.kwargs["code"]
        assert result.email == "new@example.com"

    async with session_factory() as session:
        confirm = get_confirm_email_change_usecase(session=session)
        result = await confirm.execute(user_id=user_id, code=code)
        assert result.email == "new@example.com"

    async with session_factory() as session:
        assert (await session.get(User, user_id)).email == "new@example.com"
        assert (await session.scalar(select(ExpertApplication))).email == "new@example.com"
        assert await session.get(EmailChange, user_id) is None


async def test_failed_attempts_do_not_allow_immediate_new_code(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    audit_ids: tuple[int, int, int],
) -> None:
    """Сохранить неверные попытки и выдержать интервал отправки."""

    _, user_id, _ = audit_ids
    async with session_factory() as session:
        usecase = get_request_email_change_usecase(session=session, settings=settings)
        usecase.letters.send_email_code = AsyncMock(return_value=True)
        await usecase.execute(user_id=user_id, email="new@example.com")
        correct_code = usecase.letters.send_email_code.call_args.kwargs["code"]

    wrong_code = "000000" if correct_code != "000000" else "111111"
    for _ in range(5):
        async with session_factory() as session:
            confirm = get_confirm_email_change_usecase(session=session)
            with pytest.raises(EmailChangeError, match="Неверный код"):
                await confirm.execute(user_id=user_id, code=wrong_code)
            await session.rollback()

    async with session_factory() as session:
        change = await session.get(EmailChange, user_id)
        assert change.attempts == 5

    async with session_factory() as session:
        usecase = get_request_email_change_usecase(session=session, settings=settings)
        usecase.letters.send_email_code = AsyncMock(return_value=True)
        result = await usecase.execute(user_id=user_id, email="new@example.com")
        assert result.resend_in > 0
        usecase.letters.send_email_code.assert_not_awaited()
        with pytest.raises(EmailCodeCooldownError):
            await usecase.execute(user_id=user_id, email="another@example.com")

    async with session_factory() as session:
        confirm = get_confirm_email_change_usecase(session=session)
        with pytest.raises(EmailChangeError, match="Код устарел"):
            await confirm.execute(user_id=user_id, code=correct_code)


async def test_mail_failure_does_not_report_success(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
    audit_ids: tuple[int, int, int],
) -> None:
    """Сообщить об ошибке почты и сохранить интервал отправки."""

    _, user_id, _ = audit_ids
    async with session_factory() as session:
        usecase = get_request_email_change_usecase(session=session, settings=settings)
        usecase.letters.send_email_code = AsyncMock(return_value=False)
        with pytest.raises(EmailCodeDeliveryError):
            await usecase.execute(user_id=user_id, email="new@example.com")

    async with session_factory() as session:
        assert await session.get(EmailChange, user_id) is not None


@pytest.mark.skipif(not os.environ.get("NEDRA_TEST_DATABASE_URL"), reason="Нужна PostgreSQL")
async def test_concurrent_registration_creates_one_account(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
) -> None:
    """Зарегистрировать один аккаунт при двух одинаковых запросах."""

    app = create_app(settings=settings)
    app.state.session_factory = session_factory

    async def register() -> int:
        """Подать запрос в отдельной сессии."""

        async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
            response = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": "same@example.com",
                    "password": "Password123",
                    "full_name": "Иван Иванов",
                    "phone": "+79990000001",
                },
            )
            return response.status_code

    assert sorted(await asyncio.gather(register(), register())) == [201, 409]
    async with session_factory() as session:
        assert await session.scalar(select(func.count()).select_from(User)) == 1


async def test_profile_route_rejects_invalid_token(
    *,
    session_factory: async_sessionmaker,
    settings: Settings,
) -> None:
    """Не открывать профиль по повреждённому токену."""

    app = create_app(settings=settings)
    app.state.session_factory = session_factory
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        client.cookies.set(AUTH_COOKIE, "invalid")
        assert (await client.get("/api/v1/auth/me")).status_code == 401
        client.cookies.set(AUTH_COOKIE, create_access_token(user_id=123, settings=settings))
        assert (await client.get("/api/v1/auth/me")).status_code == 401
