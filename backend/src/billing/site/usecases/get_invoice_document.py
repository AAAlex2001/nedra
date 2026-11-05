"""Скачивание счёта на оплату."""

import asyncio

from src.audit.repositories.audit_applications import AuditApplicationRepository
from src.billing.documents.invoice_pdf import (
    build_invoice_pdf,
    describe_invoice_stage,
    invoice_filename,
)
from src.billing.exceptions import InvoiceNotFoundError
from src.billing.repositories.invoices import InvoiceRepository
from src.contracts.executors import get_executor_requisites
from src.contracts.repositories.contracts import ContractRepository
from src.core.settings import Settings
from src.documents.generated_document import GeneratedDocument
from src.expertise.repositories.expertises import ExpertiseRepository
from src.payments.enums import PaymentStage
from src.payments.options import STAGE_TITLES


class GetInvoiceDocumentUseCase:
    """Счёт заказчика в PDF."""

    def __init__(
        self,
        *,
        invoices: InvoiceRepository,
        contracts: ContractRepository,
        applications: AuditApplicationRepository,
        expertises: ExpertiseRepository,
        settings: Settings,
    ) -> None:
        """Счета, условия работ и реквизиты исполнителя."""

        self.invoices = invoices
        self.contracts = contracts
        self.applications = applications
        self.expertises = expertises
        self.settings = settings

    async def execute(
        self,
        *,
        invoice_id: int,
        user_id: int,
    ) -> GeneratedDocument:
        """Создать PDF своего счёта."""

        invoice = await self.invoices.get_by_id(invoice_id=invoice_id)
        if invoice is None or not await self.invoices.belongs_to_customer(
            invoice_id=invoice_id,
            user_id=user_id,
        ):
            raise InvoiceNotFoundError()

        if invoice.audit_id is not None:
            contract = await self.contracts.get_for_audit(audit_id=invoice.audit_id)
            application = await self.applications.get(audit_id=invoice.audit_id)
            description = application.object_name if application is not None else None
            work_id = invoice.audit_id
            work_name = "аудит СУПБ"
        else:
            contract = await self.contracts.get_for_expertise(expertise_id=invoice.expertise_id)
            expertise = await self.expertises.get_by_id(expertise_id=invoice.expertise_id)
            description = expertise.object_name if expertise is not None else None
            work_id = invoice.expertise_id
            work_name = "экспертизу промышленной безопасности"

        company = get_executor_requisites(
            kind=contract.kind if contract is not None else None,
            settings=self.settings,
        )
        subject = describe_invoice_stage(
            work_id=work_id,
            stage_title=STAGE_TITLES[PaymentStage(invoice.stage)],
            work_name=work_name,
            description=description or "",
        )
        content = await asyncio.to_thread(
            build_invoice_pdf,
            invoice=invoice,
            subject=subject,
            company=company,
            font_path=self.settings.pdf_font_path,
        )
        return GeneratedDocument(
            content=content,
            filename=invoice_filename(invoice),
            content_type="application/pdf",
        )
