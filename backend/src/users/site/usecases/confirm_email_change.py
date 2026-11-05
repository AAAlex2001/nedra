"""Подтверждение нового адреса почты."""

import hmac
from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.repositories.expert_applications import ExpertApplicationRepository
from src.users.email_codes import hash_email_code
from src.users.exceptions import EmailAlreadyTakenError, EmailChangeError, UserNotFoundError
from src.users.options import EMAIL_CODE_MAX_ATTEMPTS
from src.users.repositories.email_changes import EmailChangeRepository
from src.users.repositories.users import UserRepository
from src.users.site.schemas.user import UserResponse


class ConfirmEmailChangeUseCase:
    """Смена почты после проверки кода."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        users: UserRepository,
        changes: EmailChangeRepository,
        applications: ExpertApplicationRepository,
    ) -> None:
        """Пользователи, коды и заявки экспертов."""

        self.session = session
        self.users = users
        self.changes = changes
        self.applications = applications

    async def execute(
        self,
        *,
        user_id: int,
        code: str,
    ) -> UserResponse:
        """Подтвердить новый email."""

        user = await self.users.get_for_update(user_id=user_id)

        if user is None:
            raise UserNotFoundError()

        email_change = await self.changes.get_by_user_id(user_id=user_id)

        if email_change is None:
            raise EmailChangeError("Сначала запросите код")

        if (
            email_change.expires_at <= datetime.now(UTC)
            or email_change.attempts >= EMAIL_CODE_MAX_ATTEMPTS
        ):
            raise EmailChangeError("Код устарел, запросите новый")

        code_hash = hash_email_code(
            user_id=user_id,
            code=code.strip(),
        )

        if not hmac.compare_digest(email_change.code_hash, code_hash):
            email_change.attempts += 1
            await self.changes.save(email_change=email_change)
            await self.session.commit()
            raise EmailChangeError("Неверный код")

        email = email_change.email

        if await self.users.get_by_email(email=email) is not None:
            raise EmailAlreadyTakenError()

        application = await self.applications.get_by_user_id(user_id=user_id)
        user.email = email

        if application is not None:
            application.email = email

        try:
            await self.changes.remove(email_change=email_change)
            response = UserResponse.from_model(user=user)
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()

            if await self.users.get_by_email(email=email) is not None:
                raise EmailAlreadyTakenError() from None

            raise

        return response
