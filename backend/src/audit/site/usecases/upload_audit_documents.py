"""Загрузка документов после согласования плана."""

from fastapi import UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.enums import AuditStatus
from src.audit.exceptions import (
    AuditNotFoundError,
    AuditStateError,
    InvalidAuditApplicationError,
)
from src.audit.options import AUDIT_DOCUMENTS
from src.audit.repositories.audit_documents import AuditDocumentRepository
from src.audit.repositories.audits import AuditRepository
from src.audit.schemas.audit import AuditResponse
from src.audit.site.audit_file_storage import AuditFileStorage
from src.audit.site.audit_upload_files import AuditAttachedFile
from src.notifications.models.notification import Notification
from src.notifications.repositories.notifications import NotificationRepository
from src.users.enums import UserRole
from src.users.models.user import User


class UploadAuditDocumentsUseCase:
    """Приложения к пунктам перечня."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        audits: AuditRepository,
        documents: AuditDocumentRepository,
        notifications: NotificationRepository,
        files: AuditFileStorage,
    ) -> None:
        """Аудиты, документы и уведомления."""

        self.session = session
        self.audits = audits
        self.documents = documents
        self.notifications = notifications
        self.files = files

    async def execute(
        self,
        *,
        user: User,
        audit_id: int,
        files: list[UploadFile],
        item_numbers: list[int],
    ) -> AuditResponse:
        """Загрузить документы по перечню."""

        audit = await self.audits.get_for_update(audit_id=audit_id)

        if audit is None or audit.customer_id != user.id or user.role != UserRole.CUSTOMER:
            raise AuditNotFoundError()

        if (
            audit.status not in (AuditStatus.IN_PROGRESS, AuditStatus.REMARKS)
            or audit.lead_id is None
        ):
            raise AuditStateError("Загрузка документов открывается после согласования плана аудита")

        if not files:
            raise InvalidAuditApplicationError("Приложите хотя бы один документ")

        if len(files) != len(item_numbers):
            raise InvalidAuditApplicationError("Для каждого файла нужен номер пункта перечня")

        attachments = []

        for file, number in zip(files, item_numbers, strict=True):
            if number < 1 or number > len(AUDIT_DOCUMENTS):
                raise InvalidAuditApplicationError(f"В перечне нет пункта {number}")

            attachments.append(
                AuditAttachedFile(
                    file=file,
                    kind="audit_item",
                    item_number=number,
                )
            )

        saved_documents = await self.files.save_all(attachments=attachments)

        try:
            documents = [
                document.to_model(audit_id=audit_id, uploaded_by=user.id)
                for document in saved_documents
            ]
            await self.documents.add_many(documents=documents)
            await self.notifications.add(
                notification=Notification(
                    user_id=audit.lead_id,
                    audit_id=audit_id,
                    text=f"Заказчик загрузил документы по перечню, заявка №{audit_id}",
                )
            )
            response = AuditResponse.from_model(audit=audit)
        except Exception:
            try:
                await self.session.rollback()
            finally:
                await self.files.remove_all(documents=saved_documents)

            raise

        try:
            await self.session.commit()
        except IntegrityError:
            try:
                await self.session.rollback()
            finally:
                await self.files.remove_all(documents=saved_documents)

            raise

        return response
