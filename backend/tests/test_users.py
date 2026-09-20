"""Тесты сценариев регистрации и входа без настоящей БД.

Сценарии зависят от UserRepository только через его методы, поэтому
подменяем репозиторий простым словарём в памяти.
"""

import asyncio

import pytest

from app.models.user import User, UserRole
from app.schemas.user import LoginSchema, RegisterSchema
from app.services.experts.exceptions import ApplicationPendingError
from app.services.users.exceptions import (
    EmailAlreadyTakenError,
    InvalidCredentialsError,
    InvalidPhoneError,
    WeakPasswordError,
)
from app.services.users.usecases.login import LoginUserUseCase
from app.services.users.usecases.register import RegisterUserUseCase
from app.services.users.validators import normalize_phone, validate_password


class FakeUserRepository:
    """Репозиторий в памяти: те же методы, что у настоящего, но без SQL."""

    def __init__(self) -> None:
        self.users: dict[str, User] = {}
        self.next_id = 1

    async def get_by_id(self, user_id: int) -> User | None:
        for user in self.users.values():
            if user.id == user_id:
                return user
        return None

    async def get_by_email(self, email: str) -> User | None:
        return self.users.get(email)

    async def add(self, user: User) -> User:
        if user.email in self.users:
            raise EmailAlreadyTakenError(user.email)
        user.id = self.next_id
        self.next_id = self.next_id + 1
        self.users[user.email] = user
        return user


class FakeApplicationRepository:
    """Заявки экспертов: помним только email тех, кто ждёт проверки."""

    def __init__(self, pending_emails: list[str] | None = None) -> None:
        self.pending_emails = pending_emails or []

    async def has_pending(self, email: str) -> bool:
        return email in self.pending_emails


def make_register_payload(email: str = "Ivan@Example.com") -> RegisterSchema:
    return RegisterSchema(
        email=email,
        password="secret123",
        full_name="  Иван Иванов ",
        phone="+7 (999) 000-00-00",
    )


def test_register_normalizes_and_hashes() -> None:
    repo = FakeUserRepository()
    usecase = RegisterUserUseCase(repo)

    user = asyncio.run(usecase.execute(make_register_payload()))

    assert user.id == 1
    assert user.email == "ivan@example.com"
    assert user.full_name == "Иван Иванов"
    assert user.phone == "+79990000000"
    assert user.role == UserRole.CUSTOMER
    assert user.password_hash != "secret123"


def test_register_rejects_taken_email() -> None:
    repo = FakeUserRepository()
    usecase = RegisterUserUseCase(repo)
    asyncio.run(usecase.execute(make_register_payload()))

    with pytest.raises(EmailAlreadyTakenError):
        asyncio.run(usecase.execute(make_register_payload("IVAN@example.com")))


def test_register_rejects_weak_password() -> None:
    repo = FakeUserRepository()
    usecase = RegisterUserUseCase(repo)
    payload = make_register_payload()
    payload.password = "onlyletters"

    with pytest.raises(WeakPasswordError):
        asyncio.run(usecase.execute(payload))


def test_login_success_ignores_email_case() -> None:
    repo = FakeUserRepository()
    asyncio.run(RegisterUserUseCase(repo).execute(make_register_payload()))
    usecase = LoginUserUseCase(repo, FakeApplicationRepository())

    user = asyncio.run(
        usecase.execute(LoginSchema(email="IVAN@example.com", password="secret123"))
    )

    assert user.email == "ivan@example.com"


def test_login_wrong_password() -> None:
    repo = FakeUserRepository()
    asyncio.run(RegisterUserUseCase(repo).execute(make_register_payload()))
    usecase = LoginUserUseCase(repo, FakeApplicationRepository())

    with pytest.raises(InvalidCredentialsError):
        asyncio.run(
            usecase.execute(LoginSchema(email="ivan@example.com", password="wrong123"))
        )


def test_login_unknown_email() -> None:
    usecase = LoginUserUseCase(FakeUserRepository(), FakeApplicationRepository())

    with pytest.raises(InvalidCredentialsError):
        asyncio.run(
            usecase.execute(LoginSchema(email="nobody@example.com", password="secret123"))
        )


def test_login_pending_expert() -> None:
    applications = FakeApplicationRepository(pending_emails=["expert@example.com"])
    usecase = LoginUserUseCase(FakeUserRepository(), applications)

    with pytest.raises(ApplicationPendingError):
        asyncio.run(
            usecase.execute(LoginSchema(email="Expert@example.com", password="secret123"))
        )


def test_validate_password_requires_letter_and_digit() -> None:
    validate_password("abc12345")

    with pytest.raises(WeakPasswordError):
        validate_password("12345678")

    with pytest.raises(WeakPasswordError):
        validate_password("short1")


def test_normalize_phone() -> None:
    assert normalize_phone("8 999 000 00 00") == "89990000000"
    assert normalize_phone("+7 999 000-00-00") == "+79990000000"

    with pytest.raises(InvalidPhoneError):
        normalize_phone("12345")
