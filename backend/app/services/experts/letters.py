"""Письма эксперту о решении по заявке."""

from app.config import get_settings
from app.models.expert import ExpertApplication
from app.services.mail.sender import send_email

SITE_URL = "https://nedra-npi.ru"


async def send_application_received(application: ExpertApplication) -> None:
    """Подтверждение эксперту, что заявка принята, и уведомление менеджерам."""

    settings = get_settings()

    await send_email(
        recipients=[application.email],
        subject="Заявка эксперта принята — НПИ «Недра»",
        text=(
            f"{application.full_name}, ваша заявка на регистрацию эксперта принята.\n\n"
            "Мы проверим удостоверения и напишем вам на этот адрес. "
            "Обычно проверка занимает до двух рабочих дней."
        ),
    )

    await send_email(
        recipients=settings.notify_emails,
        subject=f"Новая заявка эксперта №{application.id}",
        text=(
            f"Эксперт: {application.full_name}\n"
            f"Email: {application.email}\n"
            f"Телефон: {application.phone}\n"
            f"Удостоверений: {len(application.certificates)}\n\n"
            "Проверить заявку можно в админке, раздел «Эксперты»."
        ),
        reply_to=application.email,
    )


async def send_application_approved(application: ExpertApplication) -> None:
    """Эксперту: заявка одобрена, можно входить."""

    await send_email(
        recipients=[application.email],
        subject="Заявка одобрена — НПИ «Недра»",
        text=(
            f"{application.full_name}, ваша заявка одобрена.\n\n"
            f"Войдите на сайте {SITE_URL} с email и паролем аккаунта. Если аккаунт у вас "
            "уже был, пароль прежний. Роль эксперта включается переключателем "
            "в личном кабинете."
        ),
    )


async def send_application_rejected(application: ExpertApplication) -> None:
    """Эксперту: заявка отклонена, с причиной от админа."""

    comment = application.admin_comment or "причина не указана"

    await send_email(
        recipients=[application.email],
        subject="Заявка отклонена — НПИ «Недра»",
        text=(
            f"{application.full_name}, к сожалению, мы не можем одобрить вашу заявку.\n\n"
            f"Причина: {comment}\n\n"
            "Вы можете подать заявку повторно, исправив замечания."
        ),
    )
