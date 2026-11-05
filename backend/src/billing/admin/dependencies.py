"""Зависимости проверки банковских переводов."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.billing.admin.usecases.confirm_invoice_payment import ConfirmInvoicePaymentUseCase
from src.billing.admin.usecases.list_invoices import ListAdminInvoicesUseCase
from src.billing.repositories.invoices import InvoiceRepository
from src.core.database import get_session
from src.payments.dependencies import (
    get_audit_payment_confirmation,
    get_expertise_payment_confirmation,
)


def get_list_admin_invoices_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> ListAdminInvoicesUseCase:
    """Просмотр всех счетов."""

    return ListAdminInvoicesUseCase(invoices=InvoiceRepository(session=session))


def get_confirm_invoice_payment_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> ConfirmInvoicePaymentUseCase:
    """Подтверждение оплаты счёта."""

    return ConfirmInvoicePaymentUseCase(
        session=session,
        invoices=InvoiceRepository(session=session),
        audit_confirmation=get_audit_payment_confirmation(session=session),
        expertise_confirmation=get_expertise_payment_confirmation(session=session),
    )
