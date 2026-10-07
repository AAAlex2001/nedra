"""Письма аккаунта. Текст собирается здесь, отправляет services/mail."""

from app.services.mail.sender import send_email


async def send_email_change_code(email: str, full_name: str, code: str) -> None:
    """Код подтверждения на новый адрес."""

    await send_email(
        recipients=[email],
        subject=f"Код подтверждения email: {code}",
        text=(
            f"{full_name}, здравствуйте!\n\n"
            f"Код для смены email в личном кабинете НПИ «Недра»: {code}\n"
            "Код действует 15 минут.\n\n"
            "Если вы не меняли email, просто проигнорируйте это письмо."
        ),
    )
