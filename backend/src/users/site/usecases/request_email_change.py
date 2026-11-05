"""Запрос кода для смены почты."""

import math
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.users.contact_validation import normalize_email
from src.users.email_codes import create_email_code, hash_email_code
from src.users.exceptions import (
    EmailAlreadyTakenError,
    EmailChangeError,
    EmailCodeCooldownError,
    EmailCodeDeliveryError,
    UserNotFoundError,
)
from src.users.models.email_change import EmailChange
from src.users.options import EMAIL_CODE_LIFETIME
from src.users.repositories.email_changes import EmailChangeRepository
from src.users.repositories.users import UserRepository
from src.users.site.schemas.email_change import EmailCodeSentResponse
from src.users.site.user_letters import UserLetters


class RequestEmailChangeUseCase:
    """Подтверждение нового адреса почты."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        users: UserRepository,
        changes: EmailChangeRepository,
        letters: UserLetters,
    ) -> None:
        """Пользователи, коды и письма."""

        self.session = session
        self.users = users
        self.changes = changes
        self.letters = letters

    async def execute(
        self,
        *,
        user_id: int,
        email: str,
    ) -> EmailCodeSentResponse:
        """Отправить код на новый адрес."""

        email = normalize_email(email=email)
        user = await self.users.get_for_update(user_id=user_id)

        if user is None:
            raise UserNotFoundError()

        if email == user.email:
            raise EmailChangeError("Это ваш текущий email")

        if await self.users.get_by_email(email=email) is not None:
            raise EmailAlreadyTakenError()

        now = datetime.now(UTC)
        email_change = await self.changes.get_by_user_id(user_id=user_id)

        if email_change is not None and email_change.expires_at > now:
            resend_in = math.ceil((email_change.expires_at - now).total_seconds())

            if email_change.email != email:
                raise EmailCodeCooldownError(seconds=resend_in)

            return EmailCodeSentResponse(
                email=email,
                resend_in=resend_in,
            )

        code = create_email_code()

        if email_change is None:
            email_change = EmailChange(user_id=user_id)

        email_change.email = email
        email_change.code_hash = hash_email_code(
            user_id=user_id,
            code=code,
        )
        email_change.attempts = 0
        email_change.created_at = now
        email_change.expires_at = now + EMAIL_CODE_LIFETIME
        await self.changes.save(email_change=email_change)
        await self.session.commit()

        code_was_sent = await self.letters.send_email_code(
            email=email,
            code=code,
        )

        if not code_was_sent:
            raise EmailCodeDeliveryError()

        return EmailCodeSentResponse(
            email=email,
            resend_in=int(EMAIL_CODE_LIFETIME.total_seconds()),
        )
