"""Письма о кандидатах в комиссию."""

from src.commission.models.commission_application import CommissionApplication
from src.core.email_sender import EmailSender
from src.users.options import OBJECT_BY_CODE


class CommissionLetters:
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

    async def send_created(self, *, application: CommissionApplication) -> None:
        """Сообщить о новом кандидате."""

        attestation_lines = []

        for attestation in application.attestations:
            expertise_object = OBJECT_BY_CODE[attestation["object_code"]]
            attestation_lines.append(
                f"{attestation['area_code']} {expertise_object.label}, {attestation['category']} категория"
            )

        attestation_text = "\n".join(attestation_lines)
        text = (
            f"Заявка №{application.id} в конкурсную комиссию\n"
            f"ФИО: {application.full_name}\nТелефон: {application.phone}\n"
            f"Почта: {application.email}\nАттестации:\n{attestation_text}\n"
            f"Дата: {application.created_at:%d.%m.%Y %H:%M}"
        )

        for recipient in self.recipients:
            await self.sender.send(
                recipient=recipient,
                subject=f"Конкурсная комиссия: заявка №{application.id} — {application.full_name}",
                text=text,
                reply_to=application.email,
            )
