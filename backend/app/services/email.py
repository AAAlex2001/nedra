import logging
from email.message import EmailMessage
from html import escape

import aiosmtplib

from app.config import get_settings
from app.schemas.request import RequestOutSchema
from app.services.requestDTO import ACTIVITY_TITLES, DIRECTION_TITLES

logger = logging.getLogger(__name__)


def build_fields(request: RequestOutSchema) -> list[tuple[str, str]]:
    return [
        ("Направление", DIRECTION_TITLES.get(request.direction, "—")),
        ("Услуга", ACTIVITY_TITLES.get(request.activity, "—")),
        ("Имя", request.name),
        ("Телефон", request.telephone),
        ("Email", request.email),
        ("Организация", request.company_name or "—"),
        ("ИНН", request.inn or "—"),
        ("Задача", request.comment),
        ("Дата", request.created_at.strftime("%d.%m.%Y %H:%M")),
    ]


def build_text(request: RequestOutSchema) -> str:
    lines = [f"{label}: {value}" for label, value in build_fields(request)]

    return "Новая заявка с сайта\n\n" + "\n".join(lines)


def build_html(request: RequestOutSchema) -> str:
    rows = "".join(
        f"""
        <tr>
          <td style="padding:10px 16px;color:#7b8190;font-size:13px;
                     border-bottom:1px solid #eceef3;white-space:nowrap;
                     vertical-align:top;">{escape(label)}</td>
          <td style="padding:10px 16px;color:#0b0b0b;font-size:14px;
                     border-bottom:1px solid #eceef3;">{escape(value)}</td>
        </tr>
        """
        for label, value in build_fields(request)
    )

    return f"""
    <html>
      <body style="margin:0;padding:24px;background:#f5f6f8;
                   font-family:Arial,Helvetica,sans-serif;">
        <table style="max-width:640px;margin:0 auto;width:100%;
                      border-collapse:collapse;background:#fff;
                      border-radius:12px;overflow:hidden;">
          <tr>
            <td colspan="2" style="padding:20px 16px;background:#f69827;
                                   color:#fff;font-size:18px;font-weight:bold;">
              Заявка №{request.request_id} с сайта
            </td>
          </tr>
          {rows}
        </table>
      </body>
    </html>
    """


async def send_new_request(request: RequestOutSchema) -> None:
    settings = get_settings()

    if not settings.smtp_host or not settings.smtp_user or not settings.notify_emails:
        logger.warning("Уведомления по почте не настроены, письмо не отправлено")
        return

    direction = DIRECTION_TITLES.get(request.direction, "Заявка")

    message = EmailMessage()
    message["From"] = settings.smtp_user
    message["To"] = ", ".join(settings.notify_emails)
    message["Reply-To"] = request.email
    message["Subject"] = f"Заявка №{request.request_id} — {direction}"

    message.set_content(build_text(request))
    message.add_alternative(build_html(request), subtype="html")

    try:
        await aiosmtplib.send(
            message,
            recipients=settings.notify_emails,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            use_tls=True,
            username=settings.smtp_user,
            password=settings.smtp_password,
            timeout=15,
        )
    except Exception:
        logger.exception("Не удалось отправить письмо о заявке %s", request.request_id)
