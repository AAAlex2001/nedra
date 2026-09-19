"""Письмо менеджерам о новой заявке."""

from html import escape

from app.config import get_settings
from app.models.request import Request
from app.services.mail.sender import send_email
from app.services.requests.catalog import ACTIVITY_TITLES, DIRECTION_TITLES


def build_fields(request: Request) -> list[tuple[str, str]]:
    """Пары «подпись — значение» в том порядке, в каком они идут в письме."""

    return [
        ("Направление", DIRECTION_TITLES.get(request.direction, "—")),
        ("Услуга", ACTIVITY_TITLES.get(request.activity, "—")),
        ("Имя", request.name),
        ("Телефон", request.telephone),
        ("Email", request.email),
        ("Организация", request.company_name or "—"),
        ("ИНН", request.inn or "—"),
        ("Задача", request.comment or "—"),
        ("Дата", request.created_at.strftime("%d.%m.%Y %H:%M")),
    ]


def build_text(request: Request) -> str:
    """Текстовая версия письма для почтовых клиентов без HTML."""

    lines = [f"{label}: {value}" for label, value in build_fields(request)]

    return "Новая заявка с сайта\n\n" + "\n".join(lines)


def build_html(request: Request) -> str:
    """HTML-версия письма: таблица с полями заявки."""

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
              Заявка №{request.id} с сайта
            </td>
          </tr>
          {rows}
        </table>
      </body>
    </html>
    """


async def send_new_request_letter(request: Request) -> None:
    """Отправить менеджерам письмо о заявке. Адреса — из NOTIFY_EMAILS."""

    settings = get_settings()
    direction = DIRECTION_TITLES.get(request.direction, "Заявка")

    await send_email(
        recipients=settings.notify_emails,
        subject=f"Заявка №{request.id} — {direction}",
        text=build_text(request),
        html=build_html(request),
        reply_to=request.email,
    )
