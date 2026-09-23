"""Сценарий: заказчик сообщает, что оплатил счёт со своего расчётного счёта."""

from datetime import datetime, timezone

from fastapi import UploadFile

from app.models.billing import Invoice
from app.models.expertise import Expertise, ExpertiseDocument
from app.models.notification import Notification
from app.models.user import User
from app.services.billing.exceptions import InvoiceAlreadyPaidError, InvoiceNotFoundError
from app.services.billing.repo import InvoiceRepository
from app.services.expertise.repo import ExpertiseRepository
from app.services.files.storage import DOCUMENTATION_MAX_SIZE_BYTES, PrivateStorage
from app.services.notifications.repo import NotificationRepository

DOCUMENTS_FOLDER = "expertise-documents"

PAYMENT_ORDER = "payment_order"
GUARANTEE_LETTER = "guarantee_letter"
CHECK_PAYMENT = "check_payment"


class ReportInvoicePaidUseCase:
    """Отметить, что заказчик заявил об оплате счёта.

    Деньги идут мимо сайта, поэтому это только сигнал администратору:
    статус экспертизы двигает всё равно он, когда увидит поступление в банке.
    К заявлению можно приложить платёжное поручение, а если предоплату внести
    нечем — гарантийное письмо. Файл виден администратору в карточке заявки.
    """

    def __init__(
        self,
        invoices: InvoiceRepository,
        expertises: ExpertiseRepository,
        storage: PrivateStorage,
        notifications: NotificationRepository,
    ) -> None:
        self.invoices = invoices
        self.expertises = expertises
        self.storage = storage
        self.notifications = notifications

    async def execute(
        self,
        customer: User,
        invoice_id: int,
        document: UploadFile | None = None,
        document_kind: str = PAYMENT_ORDER,
    ) -> Invoice:
        """Бросает InvoiceNotFoundError и InvoiceAlreadyPaidError."""

        invoice = await self.invoices.get_by_id(invoice_id)
        if invoice is None:
            raise InvoiceNotFoundError(f"Счёт {invoice_id} не найден")

        expertise = await self.expertises.get_by_id(invoice.expertise_id)
        if expertise is None or expertise.customer_id != customer.id:
            raise InvoiceNotFoundError(f"Счёт {invoice_id} не найден")

        if invoice.paid_at is not None:
            raise InvoiceAlreadyPaidError("Оплата по счёту уже подтверждена")

        if document is not None:
            kind = GUARANTEE_LETTER if document_kind == GUARANTEE_LETTER else PAYMENT_ORDER
            stored = await self.storage.save(
                document, DOCUMENTS_FOLDER, DOCUMENTATION_MAX_SIZE_BYTES
            )
            expertise.documents.append(
                ExpertiseDocument(
                    uploaded_by=customer.id,
                    kind=kind,
                    file_path=stored.path,
                    original_name=stored.original_name,
                    size=stored.size,
                    content_type=stored.content_type,
                )
            )
            await self.expertises.save(expertise)

        if invoice.reported_at is not None:
            return invoice

        invoice.reported_at = datetime.now(timezone.utc)

        if expertise.expert_id is not None:
            self.notifications.add_all(
                [
                    Notification(
                        user_id=expertise.expert_id,
                        expertise_id=expertise.id,
                        kind=CHECK_PAYMENT,
                        text=f"Заказчик заявил об оплате по заявке №{expertise.id}",
                    )
                ]
            )

        return await self.invoices.save(invoice)


def invoice_expertise(expertise: Expertise) -> str:
    """Короткое описание заявки для письма администратору."""

    if expertise.area_code is None:
        return f"Заявка №{expertise.id}, область не указана"

    return f"Заявка №{expertise.id}, область {expertise.area_code}"
