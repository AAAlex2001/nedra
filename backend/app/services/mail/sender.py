"""Единственное место, где есть SMTP. Остальной код собирает текст и зовёт send_email."""

import logging
from dataclasses import dataclass
from email.message import EmailMessage

import aiosmtplib

from app.config import get_settings

logger = logging.getLogger(__name__)

TIMEOUT_SECONDS = 15


@dataclass(frozen=True)
class Attachment:
    """Файл во вложении письма."""

    filename: str
    content_type: str
    content: bytes


async def send_email(
    recipients: list[str],
    subject: str,
    text: str,
    html: str | None = None,
    reply_to: str | None = None,
    attachments: list[Attachment] | None = None,
) -> None:
    """Отправить письмо. Ошибки логируются, а не пробрасываются: письмо не должно ронять запрос."""

    settings = get_settings()

    if not settings.smtp_host or not settings.smtp_user or not recipients:
        logger.warning("Почта не настроена, письмо «%s» не отправлено", subject)
        return

    message = EmailMessage()
    message["From"] = settings.smtp_user
    message["To"] = ", ".join(recipients)
    message["Subject"] = subject
    if reply_to:
        message["Reply-To"] = reply_to

    message.set_content(text)
    if html:
        message.add_alternative(html, subtype="html")

    for attachment in attachments or []:
        maintype, subtype = attachment.content_type.split("/", 1)
        message.add_attachment(
            attachment.content, maintype=maintype, subtype=subtype, filename=attachment.filename
        )

    try:
        await aiosmtplib.send(
            message,
            recipients=recipients,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            use_tls=True,
            username=settings.smtp_user,
            password=settings.smtp_password,
            timeout=TIMEOUT_SECONDS,
        )
    except Exception:
        logger.exception("Не удалось отправить письмо «%s»", subject)
