"""Смена email: код уходит на новый адрес, адрес меняется после ввода кода."""

import hashlib
import hmac
import math
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from app.models.email_change import EmailChange
from app.models.user import User
from app.services.experts.repo import ExpertApplicationRepository
from app.services.users.email_changes import EmailChangeRepository
from app.services.users.exceptions import (
    EmailAlreadyTakenError,
    EmailChangeError,
    EmailCodeCooldownError,
)
from app.services.users.repo import UserRepository
from app.services.users.validators import normalize_email

CODE_LIFETIME = timedelta(minutes=5)
MAX_ATTEMPTS = 5


@dataclass(frozen=True)
class EmailCode:
    """Итог запроса кода. code=None — прежний код ещё действует, письмо не шлём."""

    email: str
    code: str | None
    resend_in: int


def hash_code(user_id: int, code: str) -> str:
    """Хеш кода с привязкой к пользователю: в базе код открытым текстом не лежит."""

    return hashlib.sha256(f"{user_id}:{code}".encode()).hexdigest()


def is_active(change: EmailChange, now: datetime) -> bool:
    """Код ещё можно ввести: не истёк и попытки не кончились."""

    return change.expires_at > now and change.attempts < MAX_ATTEMPTS


def seconds_left(change: EmailChange, now: datetime) -> int:
    """Сколько секунд осталось до истечения кода, с округлением вверх."""

    return math.ceil((change.expires_at - now).total_seconds())


class RequestEmailChangeUseCase:
    """Проверить новый адрес и выдать код, который уйдёт на него письмом.

    Пока прежний код действует, новый не выдаём: так письма не шлют пачками.
    """

    def __init__(self, users: UserRepository, changes: EmailChangeRepository) -> None:
        self.users = users
        self.changes = changes

    async def execute(self, user: User, email: str) -> EmailCode:
        """Бросает EmailChangeError, EmailAlreadyTakenError, EmailCodeCooldownError."""

        normalized = normalize_email(email)

        if normalized == user.email:
            raise EmailChangeError("Это ваш текущий email")

        if await self.users.get_by_email(normalized) is not None:
            raise EmailAlreadyTakenError(f"Email {normalized} уже занят")

        now = datetime.now(timezone.utc)
        current = await self.changes.get(user.id)

        if current is not None and is_active(current, now):
            resend_in = seconds_left(current, now)

            if current.email != normalized:
                raise EmailCodeCooldownError(resend_in)

            return EmailCode(email=normalized, code=None, resend_in=resend_in)

        code = f"{secrets.randbelow(10**6):06d}"

        await self.changes.put(
            EmailChange(
                user_id=user.id,
                email=normalized,
                code_hash=hash_code(user.id, code),
                attempts=0,
                expires_at=now + CODE_LIFETIME,
            )
        )

        resend_in = int(CODE_LIFETIME.total_seconds())

        return EmailCode(email=normalized, code=code, resend_in=resend_in)


class ConfirmEmailChangeUseCase:
    """Сверить код и поменять email. Попыток ограниченное число, код живёт 5 минут."""

    def __init__(
        self,
        users: UserRepository,
        changes: EmailChangeRepository,
        applications: ExpertApplicationRepository,
    ) -> None:
        self.users = users
        self.changes = changes
        self.applications = applications

    async def execute(self, user: User, code: str) -> User:
        """Бросает EmailChangeError, EmailAlreadyTakenError."""

        change = await self.changes.get(user.id)
        if change is None:
            raise EmailChangeError("Сначала запросите код")

        if not is_active(change, datetime.now(timezone.utc)):
            raise EmailChangeError("Код устарел, запросите новый")

        if not hmac.compare_digest(change.code_hash, hash_code(user.id, code.strip())):
            change.attempts += 1
            await self.changes.put(change)
            raise EmailChangeError("Неверный код")

        if await self.users.get_by_email(change.email) is not None:
            raise EmailAlreadyTakenError(f"Email {change.email} уже занят")

        user.email = change.email

        application = await self.applications.get_by_user_id(user.id)
        if application is not None:
            application.email = change.email

        await self.changes.remove(change)

        return await self.users.save(user)
