"""Письма о регистрации эксперта."""

from src.auth.models.expert_application import ExpertApplication
from src.core.email_sender import EmailSender


class ExpertApplicationLetters:
    """Письма о получении заявки эксперта."""

    def __init__(
        self,
        *,
        sender: EmailSender,
        manager_emails: list[str],
    ) -> None:
        """Отправитель и адреса получателей."""

        self.sender = sender
        self.manager_emails = manager_emails

    async def send_application_received(self, *, application: ExpertApplication) -> None:
        """Подтвердить получение заявки."""

        await self.sender.send(
            recipient=application.email,
            subject="Заявка эксперта принята — Недра",
            text=f"{application.full_name}, ваша заявка принята. Мы проверим удостоверения и напишем вам.",
        )

        for email in self.manager_emails:
            await self.sender.send(
                recipient=email,
                subject=f"Новая заявка эксперта №{application.id}",
                text=f"Эксперт: {application.full_name}\nEmail: {application.email}\n"
                f"Телефон: {application.phone}\n\nПроверить заявку можно в админке.",
            )
