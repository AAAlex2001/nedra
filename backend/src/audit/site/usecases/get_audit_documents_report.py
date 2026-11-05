"""Скачивание отчёта о документах аудита."""

import asyncio
from datetime import UTC, datetime

from src.audit.repositories.audit_applications import AuditApplicationRepository
from src.audit.repositories.audit_customers import AuditCustomerRepository
from src.audit.repositories.audit_documents import AuditDocumentRepository
from src.audit.site.audit_access import AuditAccess
from src.audit.site.documents.audit_documents_report import create_audit_documents_report
from src.documents.generated_document import GeneratedDocument
from src.documents.options import DOCX_CONTENT_TYPE
from src.users.exceptions import UserNotFoundError
from src.users.models.user import User
from src.users.repositories.users import UserRepository


class GetAuditDocumentsReportUseCase:
    """Отчёт для участника аудита."""

    def __init__(
        self,
        *,
        access: AuditAccess,
        applications: AuditApplicationRepository,
        customers: AuditCustomerRepository,
        documents: AuditDocumentRepository,
        users: UserRepository,
    ) -> None:
        """Просмотр доступных заявок."""

        self.access = access
        self.applications = applications
        self.customers = customers
        self.documents = documents
        self.users = users

    async def execute(
        self,
        *,
        audit_id: int,
        user: User,
    ) -> GeneratedDocument:
        """Создать отчёт о документах."""

        audit = await self.access.get_visible(
            audit_id=audit_id,
            user=user,
        )
        customer = await self.users.get_by_id(user_id=audit.customer_id)
        if customer is None:
            raise UserNotFoundError()

        company = await self.customers.get_company(audit_id=audit_id)
        application = await self.applications.get(audit_id=audit_id)
        documents = await self.documents.list_for_audit(audit_id=audit_id)
        customer_title = customer.full_name
        if company is not None:
            customer_title = f"{company.name}, ИНН {company.inn}"

        content = await asyncio.to_thread(
            create_audit_documents_report,
            audit_id=audit_id,
            customer_title=customer_title,
            object_name=application.object_name if application is not None else None,
            documents=documents,
            generated_at=datetime.now(UTC),
        )

        return GeneratedDocument(
            content=content,
            filename=f"Отчёт о представленных документах — заявка {audit_id}.docx",
            content_type=DOCX_CONTENT_TYPE,
        )
