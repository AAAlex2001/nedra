"""Письма по аудиту."""

from src.audit.audit_letters import AuditLetters
from src.core.email_sender import EmailSender
from src.core.settings import Settings


def get_audit_letters(*, settings: Settings) -> AuditLetters:
    """Письма участникам аудита."""

    return AuditLetters(
        sender=EmailSender(settings=settings),
        cabinet_url=settings.cabinet_url,
        manager_emails=settings.notify_emails,
    )
