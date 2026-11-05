"""Письма пользователю."""

from src.core.email_sender import EmailSender


class UserLetters:
    """Письма о настройках аккаунта."""

    def __init__(self, *, sender: EmailSender) -> None:
        """Отправитель писем."""

        self.sender = sender

    async def send_email_code(
        self,
        *,
        email: str,
        code: str,
    ) -> bool:
        """Отправить код на новый адрес."""

        return await self.sender.send(
            recipient=email,
            subject="Подтверждение нового email — Недра",
            text=f"Код подтверждения нового email: {code}\n\nВведите его в личном кабинете.",
        )
