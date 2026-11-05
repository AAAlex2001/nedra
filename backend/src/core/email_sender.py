"""Отправка писем через SMTP."""

import logging
from dataclasses import dataclass
from email.message import EmailMessage

import aiosmtplib

from src.core.options import SMTP_TIMEOUT_SECONDS
from src.core.settings import Settings


@dataclass(frozen=True)
class EmailAttachment:
    """Приложение к письму."""

    filename: str  # Имя вложения.
    content: bytes  # Содержимое вложения.
    content_type: str  # MIME-тип вложения.


class EmailSender:
    """Отправка электронной почты."""

    def __init__(self, *, settings: Settings) -> None:
        """Настройки почты."""

        self.settings = settings

    async def send(
        self,
        *,
        recipient: str,
        subject: str,
        text: str,
        attachments: list[EmailAttachment] | None = None,
        reply_to: str | None = None,
    ) -> bool:
        """Отправить письмо."""

        if not self.settings.smtp_host or not self.settings.smtp_user:
            return False

        message = EmailMessage()
        message["From"] = self.settings.smtp_user
        message["To"] = recipient
        message["Subject"] = subject

        if reply_to is not None:
            message["Reply-To"] = reply_to

        message.set_content(text)

        for attachment in attachments or []:
            main_type, sub_type = attachment.content_type.split(
                "/",
                maxsplit=1,
            )
            message.add_attachment(
                attachment.content,
                maintype=main_type,
                subtype=sub_type,
                filename=attachment.filename,
            )

        try:
            await aiosmtplib.send(
                message,
                hostname=self.settings.smtp_host,
                port=self.settings.smtp_port,
                username=self.settings.smtp_user,
                password=self.settings.smtp_password,
                use_tls=self.settings.smtp_port == 465,
                timeout=SMTP_TIMEOUT_SECONDS,
            )
        except (aiosmtplib.SMTPException, OSError, TimeoutError):
            logging.getLogger(__name__).warning("Не удалось отправить письмо через SMTP")

            return False

        return True
