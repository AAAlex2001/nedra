"""Письма о новых обращениях."""

from src.core.email_sender import EmailSender
from src.requests.models.contact_request import ContactRequest
from src.requests.options import ACTIVITY_TITLES, DIRECTION_TITLES


class ContactRequestLetters:
    """Уведомления менеджерам."""

    def __init__(
        self,
        *,
        sender: EmailSender,
        recipients: list[str],
    ) -> None:
        """Почта и адреса менеджеров."""

        self.sender = sender
        self.recipients = recipients

    async def send_created(self, *, contact_request: ContactRequest) -> None:
        """Сообщить о новом обращении."""

        direction = DIRECTION_TITLES[contact_request.direction]
        activity = ACTIVITY_TITLES[contact_request.activity]
        text = (
            f"Обращение №{contact_request.id}\n"
            f"Направление: {direction}\nУслуга: {activity}\n"
            f"Имя: {contact_request.name}\nТелефон: {contact_request.telephone}\n"
            f"Почта: {contact_request.email}\nКомпания: {contact_request.company_name or '—'}\n"
            f"ИНН: {contact_request.inn or '—'}\nКомментарий: {contact_request.comment or '—'}\n"
            f"Дата: {contact_request.created_at:%d.%m.%Y %H:%M}"
        )

        for recipient in self.recipients:
            await self.sender.send(
                recipient=recipient,
                subject=f"Заявка №{contact_request.id} — {direction}",
                text=text,
                reply_to=contact_request.email,
            )
