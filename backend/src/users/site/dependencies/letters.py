"""Письма эксперту."""

from src.core.email_sender import EmailSender
from src.core.settings import Settings
from src.users.site.expert_letters import ExpertLetters


def get_expert_letters(*, settings: Settings) -> ExpertLetters:
    """Письма менеджерам об удостоверениях."""

    return ExpertLetters(
        sender=EmailSender(settings=settings),
        manager_emails=settings.notify_emails,
    )
