"""Шаг 8б: заказчик исправил замечания и отправляет документацию повторно."""

from datetime import datetime, timezone

from fastapi import UploadFile

from app.models.expertise import Expertise, ExpertiseDocument, ExpertiseStatus
from app.models.notification import Notification
from app.models.user import User
from app.services.expertise.exceptions import (
    ExpertiseAccessError,
    ExpertiseStateError,
    InvalidExpertiseError,
)
from app.services.expertise.repo import ExpertiseRepository
from app.services.files.storage import DOCUMENTATION_MAX_SIZE_BYTES, PrivateStorage
from app.services.notifications.repo import NotificationRepository

REVISIONS_FOLDER = "expertise-revisions"


class ResubmitDocumentationUseCase:
    """Принять исправленную документацию и вернуть экспертизу в работу.

    Последнее замечание закрывается датой, экспертиза снова в статусе in_progress.
    Дальше эксперт либо выдаёт новые замечания, либо готовит заключение.
    """

    def __init__(
        self,
        expertises: ExpertiseRepository,
        notifications: NotificationRepository,
        storage: PrivateStorage,
    ) -> None:
        self.expertises = expertises
        self.notifications = notifications
        self.storage = storage

    async def execute(
        self,
        customer: User,
        expertise: Expertise,
        text: str | None,
        files: list[UploadFile],
    ) -> Expertise:
        """Бросает ExpertiseStateError, ExpertiseAccessError, InvalidExpertiseError, UploadError."""

        if expertise.customer_id != customer.id:
            raise ExpertiseAccessError("Отправить исправления может только заказчик этой заявки")

        if expertise.status != ExpertiseStatus.REMARKS or expertise.expert_id is None:
            raise ExpertiseStateError("Сейчас исправления не ожидаются")

        if not files:
            raise InvalidExpertiseError("Приложите исправленную документацию")

        open_remark = next((remark for remark in expertise.remarks if remark.resolved_at is None), None)
        comment = text.strip() if text else None

        for file in files:
            stored = await self.storage.save(file, REVISIONS_FOLDER, DOCUMENTATION_MAX_SIZE_BYTES)
            document = ExpertiseDocument(
                uploaded_by=customer.id,
                kind="revision",
                file_path=stored.path,
                original_name=stored.original_name,
                size=stored.size,
                content_type=stored.content_type,
            )
            expertise.documents.append(document)
            if open_remark is not None:
                open_remark.documents.append(document)

        for remark in expertise.remarks:
            if remark.resolved_at is None:
                remark.response_text = comment
                remark.resolved_at = datetime.now(timezone.utc)

        expertise.status = ExpertiseStatus.IN_PROGRESS

        self.notifications.add_all(
            [
                Notification(
                    user_id=expertise.expert_id,
                    expertise_id=expertise.id,
                    text=f"Заказчик исправил замечания по заявке №{expertise.id} и прислал документацию повторно",
                )
            ]
        )

        return await self.expertises.save(expertise)
