"""Отправить замечания заказчику."""

from fastapi import UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.expertise.enums import ExpertiseStatus
from src.expertise.exceptions import (
    ExpertiseNotFoundError,
    ExpertiseStateError,
    InvalidExpertiseError,
)
from src.expertise.models.expertise_remark import ExpertiseRemark
from src.expertise.repositories.expertise_documents import ExpertiseDocumentRepository
from src.expertise.repositories.expertise_remarks import ExpertiseRemarkRepository
from src.expertise.repositories.expertises import ExpertiseRepository
from src.expertise.schemas.expertise import ExpertiseResponse
from src.expertise.site.expertise_file_storage import (
    ExpertiseAttachment,
    ExpertiseFileStorage,
)
from src.notifications.email_delivery import NotificationEmailDelivery
from src.notifications.models.notification import Notification
from src.notifications.repositories.notifications import NotificationRepository
from src.users.enums import UserRole
from src.users.models.user import User


class SendExpertiseRemarksUseCase:
    """Отправить замечания заказчику."""

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
        """Отправить замечания заказчику."""

        expertise = await self.expertises.get_for_update(expertise_id=expertise_id)

        if expertise is None or expertise.expert_id != user.id or user.role != UserRole.EXPERT:
            raise ExpertiseNotFoundError()

        if expertise.status != ExpertiseStatus.IN_PROGRESS:
            raise ExpertiseStateError("Действие недоступно на этом этапе")

        text = text.strip() if text else None

        if not text and not files:
            raise InvalidExpertiseError("Напишите замечания или приложите файл")

        notification = Notification(
            user_id=expertise.customer_id,
            expertise_id=expertise_id,
            text=f"Получены замечания, №{expertise_id}",
        )

        attachments = [
            ExpertiseAttachment(
                file=file,
                kind="remarks",
            )
            for file in files
        ]
        saved_documents = await self.file_storage.save_all(attachments=attachments)

        try:
            remark = ExpertiseRemark(
                expertise_id=expertise_id,
                text=text,
            )
            await self.remarks.add(remark=remark)

            documents = [
                document.to_model(
                    expertise_id=expertise_id, uploaded_by=user.id, remark_id=remark.id
                )
                for document in saved_documents
            ]
            await self.documents.add_many(documents=documents)

            expertise.status = ExpertiseStatus.REMARKS
            await self.expertises.save(expertise=expertise)
            await self.notifications.add(notification=notification)
            response = ExpertiseResponse.from_model(expertise=expertise)
        except Exception:
            try:
                await self.session.rollback()
            finally:
                await self.file_storage.remove_all(documents=saved_documents)

            raise

        try:
            await self.session.commit()
        except IntegrityError:
            try:
                await self.session.rollback()
            finally:
                await self.file_storage.remove_all(documents=saved_documents)

            raise

        await self.email_delivery.send(notification=notification)

        return response
