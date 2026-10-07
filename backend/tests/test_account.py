import asyncio
from datetime import datetime, timedelta, timezone

import pytest

from app.models.email_change import EmailChange
from app.models.user import User, UserRole
from app.services.users.exceptions import EmailAlreadyTakenError, EmailChangeError
from app.services.users.usecases.change_email import (
    ConfirmEmailChangeUseCase,
    RequestEmailChangeUseCase,
)
from app.services.users.usecases.update_profile import UpdateProfileUseCase


class FakeUserRepository:
    def __init__(self, users: list[User]) -> None:
        self.users = users

    async def get_by_email(self, email: str) -> User | None:
        return next((user for user in self.users if user.email == email), None)

    async def save(self, user: User) -> User:
        return user


class FakeChangeRepository:
    def __init__(self) -> None:
        self.items: dict[int, EmailChange] = {}

    async def get(self, user_id: int) -> EmailChange | None:
        return self.items.get(user_id)

    async def put(self, change: EmailChange) -> None:
        self.items[change.user_id] = change

    async def remove(self, change: EmailChange) -> None:
        self.items.pop(change.user_id, None)


class FakeApplicationRepository:
    async def get_by_user_id(self, user_id: int) -> None:
        return None


def make_user(user_id: int, email: str) -> User:
    return User(id=user_id, email=email, password_hash="x", full_name="Иван", phone="+79990000000", role=UserRole.EXPERT)


def test_update_profile_normalizes_phone() -> None:
    user = make_user(1, "ivan@mail.ru")
    usecase = UpdateProfileUseCase(FakeUserRepository([user]), FakeApplicationRepository())

    updated = asyncio.run(usecase.execute(user, "  Пётр Петров ", "+7 (912) 345-67-89"))

    assert updated.full_name == "Пётр Петров"
    assert updated.phone == "+79123456789"


def test_email_change_with_correct_code() -> None:
    user = make_user(1, "ivan@mail.ru")
    users = FakeUserRepository([user])
    changes = FakeChangeRepository()

    email, code = asyncio.run(RequestEmailChangeUseCase(users, changes).execute(user, " New@Mail.ru "))
    assert email == "new@mail.ru"
    assert len(code) == 6

    confirm = ConfirmEmailChangeUseCase(users, changes, FakeApplicationRepository())
    updated = asyncio.run(confirm.execute(user, code))

    assert updated.email == "new@mail.ru"
    assert changes.items == {}


def test_email_change_rejects_taken_and_same() -> None:
    user = make_user(1, "ivan@mail.ru")
    users = FakeUserRepository([user, make_user(2, "busy@mail.ru")])
    request = RequestEmailChangeUseCase(users, FakeChangeRepository())

    with pytest.raises(EmailAlreadyTakenError):
        asyncio.run(request.execute(user, "busy@mail.ru"))

    with pytest.raises(EmailChangeError):
        asyncio.run(request.execute(user, "IVAN@mail.ru"))


def test_email_change_limits_attempts_and_lifetime() -> None:
    user = make_user(1, "ivan@mail.ru")
    users = FakeUserRepository([user])
    changes = FakeChangeRepository()
    email, code = asyncio.run(RequestEmailChangeUseCase(users, changes).execute(user, "new@mail.ru"))
    confirm = ConfirmEmailChangeUseCase(users, changes, FakeApplicationRepository())
    wrong = "000000" if code != "000000" else "111111"

    for attempt in range(5):
        with pytest.raises(EmailChangeError):
            asyncio.run(confirm.execute(user, wrong))

    with pytest.raises(EmailChangeError):
        asyncio.run(confirm.execute(user, code))

    email, fresh = asyncio.run(RequestEmailChangeUseCase(users, changes).execute(user, email))
    changes.items[1].expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)

    with pytest.raises(EmailChangeError):
        asyncio.run(confirm.execute(user, fresh))

    assert user.email == "ivan@mail.ru"
