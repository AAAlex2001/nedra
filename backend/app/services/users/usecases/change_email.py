"""Смена email: код уходит на новый адрес, адрес меняется после ввода кода."""

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

from app.models.email_change import EmailChange
from app.models.user import User
from app.services.experts.repo import ExpertApplicationRepository
from app.services.users.email_changes import EmailChangeRepository
from app.services.users.exceptions import EmailAlreadyTakenError, EmailChangeError
from app.services.users.repo import UserRepository
from app.services.users.validators import normalize_email

CODE_LIFETIME = timedelta(minutes=15)
MAX_ATTEMPTS = 5


def hash_code(user_id: int, code: str) -> str:
    """Хеш кода с привязкой к пользователю: в базе код открытым текстом не лежит."""

    return hashlib.sha256(f"{user_id}:{code}".encode()).hexdigest()


class RequestEmailChangeUseCase:
    """Проверить новый адрес и выдать код, который уйдёт на него письмом."""

    def __init__(self, users: UserRepository, changes: EmailChangeRepository) -> None:
        self.users = users
        self.changes = changes

    async def execute(self, user: User, email: str) -> tuple[str, str]:
        """Вернуть нормализованный адрес и код. Бросает EmailChangeError, EmailAlreadyTakenError."""

        normalized = normalize_email(email)

        if normalized == user.email:
            raise EmailChangeError("Это ваш текущий email")

        if await self.users.get_by_email(normalized) is not None:
            raise EmailAlreadyTakenError(f"Email {normalized} уже занят")

        code = f"{secrets.randbelow(10**6):06d}"

        await self.changes.put(
            EmailChange(
                user_id=user.id,
                email=normalized,
                code_hash=hash_code(user.id, code),
                attempts=0,
                expires_at=datetime.now(timezone.utc) + CODE_LIFETIME,
            )
        )

        return normalized, code


class ConfirmEmailChangeUseCase:
    """Сверить код и поменять email. Попыток ограниченное число, код живёт 15 минут."""

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

        if change.expires_at < datetime.now(timezone.utc) or change.attempts >= MAX_ATTEMPTS:
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
