"""Письма по счетам. Адреса администраторов — в NOTIFY_EMAILS."""

from app.config import get_settings
from app.models.billing import Invoice
from app.services.mail.sender import send_email


async def send_invoice_reported_letter(invoice: Invoice, number: str) -> None:
    """Администратору: заказчик сообщил, что оплатил счёт. Нужно проверить поступление."""

    settings = get_settings()

    await send_email(
        recipients=settings.notify_emails,
        subject=f"Счёт № {number} — заказчик сообщил об оплате",
        text=(
            f"{invoice.payer_name} (ИНН {invoice.payer_inn}) сообщил, что оплатил "
            f"счёт № {number} на сумму {invoice.amount} ₽ по заявке №{invoice.expertise_id}.\n\n"
            "Проверьте поступление на расчётный счёт и отметьте оплату в админке, "
            "в разделе «Счета»."
        ),
    )
