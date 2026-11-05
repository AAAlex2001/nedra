"""Отправить исправленные документы."""

from datetime import UTC, datetime

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.expertise.enums import ExpertiseStatus
from src.expertise.exceptions import (
    ExpertiseNotFoundError,
    ExpertiseStateError,
    InvalidExpertiseError,
)
from src.expertise.models.expertise_document import ExpertiseDocument
from src.expertise.repositories.expertise_documents import ExpertiseDocumentRepository
from src.expertise.repositories.expertise_remarks import ExpertiseRemarkRepository
from src.expertise.repositories.expertises import ExpertiseRepository
from src.expertise.schemas.expertise import ExpertiseResponse
from src.expertise.site.expertise_file_storage import ExpertiseAttachment, ExpertiseFileStorage
from src.notifications.email_delivery import NotificationEmailDelivery
from src.notifications.models.notification import Notification
from src.notifications.repositories.notifications import NotificationRepository
from src.users.enums import UserRole
from src.users.models.user import User


class ResubmitExpertiseDocumentsUseCase:
    """Отправить исправленные документы."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        expertises: ExpertiseRepository,
        notifications: NotificationRepository,
        email_delivery: NotificationEmailDelivery,
        documents: ExpertiseDocumentRepository,
        file_storage: ExpertiseFileStorage,
        remarks: ExpertiseRemarkRepository,
    ) -> None:
        """Хранение и уведомления."""

        self.session = session
        self.expertises = expertises
        self.notifications = notifications
        self.email_delivery = email_delivery
        self.documents = documents
        self.file_storage = file_storage
        self.remarks = remarks

    async def execute(
        self,
        *,
        expertise_id: int,
        user: User,
        files: list[UploadFile],
        text: str | None = None,
    ) -> ExpertiseResponse:
        """Отправить исправленные документы."""

        expertise = await self.expertises.get_for_update(expertise_id=expertise_id)

        if expertise is None or expertise.customer_id != user.id or user.role != UserRole.CUSTOMER:
            raise ExpertiseNotFoundError()

        if expertise.status != ExpertiseStatus.REMARKS:
            raise ExpertiseStateError("Действие недоступно на этом этапе")

        if expertise.expert_id is None:
            raise ExpertiseStateError("Исполнитель не назначен")

        text = text.strip() if text else None

        if not files:
            raise InvalidExpertiseError("Приложите хотя бы один документ")

        open_remarks = await self.remarks.list_open(expertise_id=expertise_id)

        if not open_remarks:
            raise ExpertiseStateError("Нет замечаний для исправления")

        notification = Notification(
            user_id=expertise.expert_id,
            expertise_id=expertise_id,
            text=f"Заказчик исправил документы, №{expertise_id}",
        )

        attachments = [
            ExpertiseAttachment(
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
                ExpertiseDocument(
                    expertise_id=expertise_id,
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

            expertise.status = ExpertiseStatus.IN_PROGRESS
            await self.expertises.save(expertise=expertise)
            await self.notifications.add(notification=notification)
            response = ExpertiseResponse.from_model(expertise=expertise)
        except Exception:
            try:
                await self.session.rollback()
            finally:
                await self.file_storage.remove_all(documents=saved_documents)

            raise

        await self.session.commit()
        await self.email_delivery.send(notification=notification)

        return response
