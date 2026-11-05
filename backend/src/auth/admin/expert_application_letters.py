"""Письма о решении по заявке эксперта."""

from src.auth.models.expert_application import ExpertApplication
from src.core.email_sender import EmailSender


class ExpertApplicationReviewLetters:
    """Уведомления о рассмотрении заявки."""

    def __init__(
        self,
        *,
        sender: EmailSender,
        site_url: str,
    ) -> None:
        """Отправитель и адрес сайта."""

        self.sender = sender
        self.site_url = site_url

    async def send_application_approved(self, *, application: ExpertApplication) -> None:
        """Сообщить об одобрении заявки."""

        await self.sender.send(
            recipient=application.email,
            subject="Заявка эксперта одобрена — Недра",
            text=f"{application.full_name}, ваша заявка одобрена.\n\n"
            f"Войдите на {self.site_url} с почтой и паролем, указанными в заявке.",
        )

    async def send_application_rejected(self, *, application: ExpertApplication) -> None:
        """Сообщить причину отклонения."""

        await self.sender.send(
            recipient=application.email,
            subject="Заявка эксперта отклонена — Недра",
            text=f"{application.full_name}, заявка отклонена.\n\n"
            f"Причина: {application.admin_comment}\n\nВы можете исправить замечания и подать заявку повторно.",
        )
