"""Уведомления о безналичной оплате."""

from src.billing.models.invoice import Invoice
from src.core.email_sender import EmailSender


class InvoiceLetters:
    """Письма менеджерам о заявленной оплате."""

    def __init__(
        self,
        *,
        sender: EmailSender,
        recipients: list[str],
    ) -> None:
        """Почта и адреса менеджеров."""

        self.sender = sender
        self.recipients = recipients

    async def send_payment_report(self, *, invoice: Invoice) -> None:
        """Сообщить о необходимости проверить поступление."""

        number = f"{invoice.created_at.year}-{invoice.id:04d}"
        for recipient in self.recipients:
            await self.sender.send(
                recipient=recipient,
                subject=f"Заявлена оплата счёта №{number}",
                text=f"{invoice.payer_name} сообщает об оплате {invoice.amount} ₽. Проверьте поступление и подтвердите счёт в административной панели.",
            )
