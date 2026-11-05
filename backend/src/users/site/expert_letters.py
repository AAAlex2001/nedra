"""Письма об удостоверениях эксперта."""

from src.core.email_sender import EmailSender
from src.users.models.expert_certificate import ExpertCertificate
from src.users.models.user import User


class ExpertLetters:
    """Уведомления менеджерам об аттестации."""

    def __init__(
        self,
        *,
        sender: EmailSender,
        manager_emails: list[str],
    ) -> None:
        """Отправитель и адреса менеджеров."""

        self.sender = sender
        self.manager_emails = manager_emails

    async def send_certificate_changed(
        self,
        *,
        user: User,
        certificate: ExpertCertificate,
        action: str,
    ) -> None:
        """Сообщить об изменении удостоверения."""

        for email in self.manager_emails:
            await self.sender.send(
                recipient=email,
                subject=f"Эксперт {user.full_name} {action} удостоверение",
                text=f"Эксперт: {user.full_name}\nEmail: {user.email}\n"
                f"Удостоверение: {certificate.area_code}, {certificate.object_code}\n"
                f"Категория: {certificate.category}\nСрок: {certificate.valid_until:%d.%m.%Y}\n"
                f"Номер: {certificate.number or '—'}\n\nПроверьте сведения в реестре.",
            )
