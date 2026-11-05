"""Доставка уведомлений по почте."""

from src.core.email_sender import EmailSender
from src.notifications.models.notification import Notification
from src.users.repositories.users import UserRepository


class NotificationEmailDelivery:
    """Почтовая копия уведомления."""

    def __init__(
        self,
        *,
        users: UserRepository,
        sender: EmailSender,
        cabinet_url: str,
    ) -> None:
        """Получатели и отправитель."""

        self.users = users
        self.sender = sender
        self.cabinet_url = cabinet_url

    async def send(self, *, notification: Notification) -> None:
        """Отправить сохранённое уведомление."""

        recipient = await self.users.get_by_id(user_id=notification.user_id)

        if recipient is None:
            return

        await self.sender.send(
            recipient=recipient.email,
            subject=notification.text,
            text=f"{notification.text}\n\nЛичный кабинет: {self.cabinet_url}",
        )
