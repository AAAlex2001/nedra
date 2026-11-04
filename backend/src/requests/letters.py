"""Письма, связанные с заявками."""

from src.core.config import get_settings
from src.mail.sender import send_email
from src.requests.catalog import ACTIVITY_TITLES, DIRECTION_TITLES
from src.requests.models import Request


async def send_new_request_letter(*, request: Request) -> None:
    """Отправляет менеджерам письмо о новой заявке."""

    settings = get_settings()
    recipients = settings.notify_emails
    if not recipients:
        return

    activity_title = ACTIVITY_TITLES.get(request.activity, request.activity)
    direction_title = DIRECTION_TITLES.get(request.direction, request.direction)

    text = (
        f"Новая заявка с сайта\n\n"
        f"Имя: {request.name}\n"
        f"Телефон: {request.telephone}\n"
        f"Email: {request.email}\n"
        f"Вид деятельности: {activity_title}\n"
        f"Направление: {direction_title}\n"
        f"Компания: {request.company_name or '-'}\n"
        f"ИНН: {request.inn or '-'}\n"
        f"Комментарий: {request.comment or '-'}\n"
    )

    html = (
        f"<p><b>Новая заявка с сайта</b></p>"
        f"<p>Имя: {request.name}<br>"
        f"Телефон: {request.telephone}<br>"
        f"Email: {request.email}<br>"
        f"Вид деятельности: {activity_title}<br>"
        f"Направление: {direction_title}<br>"
        f"Компания: {request.company_name or '-'}<br>"
        f"ИНН: {request.inn or '-'}<br>"
        f"Комментарий: {request.comment or '-'}</p>"
    )

    await send_email(
        to=recipients,
        subject="Новая заявка с сайта",
        text=text,
        html=html,
    )
