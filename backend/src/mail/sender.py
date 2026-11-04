"""Отправка email через SMTP."""

import logging
from dataclasses import dataclass
from email.message import EmailMessage

import aiosmtplib

from src.core.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class Attachment:
    """Вложение к письму."""

    filename: str
    content: bytes
    content_type: str = "application/octet-stream"


async def send_email(
    *,
    to: list[str],
    subject: str,
    text: str,
    html: str | None = None,
    reply_to: str | None = None,
    attachments: list[Attachment] | None = None,
) -> None:
    """Отправляет email через SMTP, не пробрасывая ошибки."""

    settings = get_settings()
    if not settings.smtp_host or not to:
        logger.warning("SMTP не настроен или нет получателей.")
        return

    message = EmailMessage()
    message["From"] = settings.smtp_user or "noreply@localhost"
    message["To"] = ", ".join(to)
    message["Subject"] = subject
    if reply_to:
        message["Reply-To"] = reply_to
    message.set_content(text)
    if html:
        message.add_alternative(html, subtype="html")

    for attachment in attachments or []:
        message.add_attachment(
            attachment.content,
            maintype=attachment.content_type.split("/")[0],
            subtype=attachment.content_type.split("/")[-1],
            filename=attachment.filename,
        )

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user or None,
            password=settings.smtp_password or None,
            use_tls=True,
            timeout=15,
        )
    except (aiosmtplib.SMTPException, OSError, TimeoutError) as exc:
        logger.error("Ошибка отправки email: %s", exc)
