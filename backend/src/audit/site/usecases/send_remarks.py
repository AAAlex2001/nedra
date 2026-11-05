"""Отправить замечания заказчику."""

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.enums import AuditStatus
from src.audit.exceptions import AuditNotFoundError, AuditStateError, InvalidAuditApplicationError
from src.audit.models.audit_document import AuditDocument
from src.audit.models.audit_remark import AuditRemark
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


class SendAuditRemarksUseCase:
    """Отправить замечания заказчику."""

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
        """Отправить замечания заказчику."""

        audit = await self.audits.get_for_update(audit_id=audit_id)

        if audit is None or audit.lead_id != user.id or user.role != UserRole.EXPERT:
            raise AuditNotFoundError()

        if audit.status != AuditStatus.IN_PROGRESS:
            raise AuditStateError("Действие недоступно на этом этапе")

        text = text.strip() if text else None

        if not text and not files:
            raise InvalidAuditApplicationError("Напишите замечания или приложите файл")

        notification = Notification(
            user_id=audit.customer_id,
            audit_id=audit_id,
            text=f"Получены замечания, №{audit_id}",
        )

        attachments = [
            AuditAttachedFile(
                file=file,
                kind="remarks",
            )
            for file in files
        ]
        saved_documents = await self.file_storage.save_all(attachments=attachments)

        try:
            remark = AuditRemark(
                audit_id=audit_id,
                text=text,
            )
            await self.remarks.add(remark=remark)

            documents = [
                AuditDocument(
                    audit_id=audit_id,
                    remark_id=remark.id,
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

            audit.status = AuditStatus.REMARKS
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
