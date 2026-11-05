"""Письма об экспертизе."""

from src.core.email_sender import EmailSender


class ExpertiseLetters:
    """Уведомления участников экспертизы."""

    def __init__(
        self,
        *,
        sender: EmailSender,
        cabinet_url: str,
    ) -> None:
        """Отправитель и адрес кабинета."""

        self.sender = sender
        self.cabinet_url = cabinet_url

    async def send_new_request(
        self,
        *,
        expertise_id: int,
        object_name: str,
        recipients: list[str],
    ) -> None:
        """Сообщить экспертам о новой заявке."""

        for recipient in recipients:
            await self.sender.send(
                recipient=recipient,
                subject=f"Новая заявка на экспертизу №{expertise_id}",
                text=f"Документация: {object_name}\n\nЛичный кабинет: {self.cabinet_url}",
            )

    async def send_expert_ready(
        self,
        *,
        expertise_id: int,
        recipient: str,
        expert_name: str,
    ) -> None:
        """Сообщить о готовности эксперта."""

        await self.sender.send(
            recipient=recipient,
            subject=f"Исполнитель готов выполнить заявку №{expertise_id}",
            text=(
                f"{expert_name} готов провести работу. Ознакомьтесь с договором в личном кабинете."
                f"\n\nЛичный кабинет: {self.cabinet_url}"
            ),
        )
