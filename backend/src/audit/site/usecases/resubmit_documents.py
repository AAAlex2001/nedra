"""Отправить исправленные документы."""

from datetime import UTC, datetime

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.enums import AuditStatus
from src.audit.exceptions import AuditNotFoundError, AuditStateError, InvalidAuditApplicationError
from src.audit.models.audit_document import AuditDocument
from src.audit.repositories.audit_documents import AuditDocumentRepository
from src.audit.repositories.audit_remarks import AuditRemarkRepository
from src.audit.repositories.audits import AuditRepository
from src.audit.schemas.audit import AuditResponse
from src.audit.site.audit_file_storage import AuditFileStorage
from src.audit.site.audit_upload_files import AuditAttachedFile
from src.notifications.email_delivery import NotificationEmailDelivery
from src.notifications.models.notification import Notification
from src.notifications.repositories.notifications import NotificationRepository
from src.users.enums import UserRole
from src.users.models.user import User


class ResubmitAuditDocumentsUseCase:
    """Отправить исправленные документы."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        audits: AuditRepository,
        notifications: NotificationRepository,
        email_delivery: NotificationEmailDelivery,
        documents: AuditDocumentRepository,
        file_storage: AuditFileStorage,
        remarks: AuditRemarkRepository,
    ) -> None:
        """Хранение и уведомления."""

        self.session = session
        self.audits = audits
        self.notifications = notifications
        self.email_delivery = email_delivery
        self.documents = documents
        self.file_storage = file_storage
        self.remarks = remarks

    async def execute(
        self,
        *,
        audit_id: int,
        user: User,
        files: list[UploadFile],
        text: str | None = None,
    ) -> AuditResponse:
        """Отправить исправленные документы."""

        audit = await self.audits.get_for_update(audit_id=audit_id)

        if audit is None or audit.customer_id != user.id or user.role != UserRole.CUSTOMER:
            raise AuditNotFoundError()

        if audit.status != AuditStatus.REMARKS:
            raise AuditStateError("Действие недоступно на этом этапе")

        if audit.lead_id is None:
            raise AuditStateError("Исполнитель не назначен")

        text = text.strip() if text else None

        if not files:
            raise InvalidAuditApplicationError("Приложите хотя бы один документ")

        open_remarks = await self.remarks.list_open(audit_id=audit_id)

        if not open_remarks:
            raise AuditStateError("Нет замечаний для исправления")

        notification = Notification(
            user_id=audit.lead_id,
            audit_id=audit_id,
            text=f"Заказчик исправил документы, №{audit_id}",
        )

        attachments = [
            AuditAttachedFile(
                file=file,
                kind="revision",
            )
            for file in files
        ]
        saved_documents = await self.file_storage.save_all(attachments=attachments)

        try:
            resolved_at = datetime.now(UTC)

            for remark in open_remarks:
                remark.response_text = text
                remark.resolved_at = resolved_at

            documents = [
                AuditDocument(
                    audit_id=audit_id,
                    remark_id=open_remarks[0].id,
                    uploaded_by=user.id,
                    kind=document.kind,
                    file_path=document.file.path,
                    original_name=document.file.original_name,
                    size=document.file.size,
                    content_type=document.file.content_type,
                )
                for document in saved_documents
            ]
            await self.documents.add_many(documents=documents)

            audit.status = AuditStatus.IN_PROGRESS
            await self.audits.save(audit=audit)
            await self.notifications.add(notification=notification)
            response = AuditResponse.from_model(audit=audit)
        except Exception:
            try:
                await self.session.rollback()
            finally:
                await self.file_storage.remove_all(documents=saved_documents)

            raise

        await self.session.commit()
        await self.email_delivery.send(notification=notification)

        return response
