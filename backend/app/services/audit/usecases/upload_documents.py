"""Заказчик загружает документы по перечню после согласования Плана аудита."""

from fastapi import UploadFile

from app.models.expertise import Expertise, ExpertiseDocument, ExpertiseStatus, ServiceKind
from app.models.notification import Notification
from app.models.user import User
from app.services.audit.checklist import AUDIT_DOCUMENTS
from app.services.audit.files import save_audit_file
from app.services.expertise.exceptions import (
    ExpertiseAccessError,
    ExpertiseStateError,
    InvalidExpertiseError,
)
from app.services.expertise.repo import ExpertiseRepository
from app.services.expertise.usecases.create_expertise import DOCUMENTS_FOLDER
from app.services.files.storage import PrivateStorage
from app.services.notifications.repo import NotificationRepository

UPLOAD_STATUSES = (ExpertiseStatus.IN_PROGRESS, ExpertiseStatus.REMARKS)


class UploadAuditDocumentsUseCase:
    """Приложить файлы к пунктам перечня, пока аудитор проверяет документы."""

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
        self, customer: User, audit: Expertise, files: list[UploadFile], items: list[int]
    ) -> Expertise:
        """Бросает ExpertiseAccessError, ExpertiseStateError, InvalidExpertiseError, UploadError."""

        if audit.service != ServiceKind.AUDIT:
            raise InvalidExpertiseError("Перечень документов есть только у аудита")

        if audit.customer_id != customer.id:
            raise ExpertiseAccessError("Загрузить документы может только заказчик этой заявки")

        if audit.status not in UPLOAD_STATUSES or audit.expert_id is None:
            raise ExpertiseStateError("Загрузка документов открывается после согласования Плана аудита")

        if not files:
            raise InvalidExpertiseError("Приложите хотя бы один документ")

        if len(files) != len(items):
            raise InvalidExpertiseError("Для каждого файла нужен номер пункта перечня")

        for number in items:
            if number < 1 or number > len(AUDIT_DOCUMENTS):
                raise InvalidExpertiseError(f"В перечне нет пункта {number}")

        for file, number in zip(files, items):
            stored = await save_audit_file(self.storage, file, DOCUMENTS_FOLDER)
            audit.documents.append(
                ExpertiseDocument(
                    uploaded_by=customer.id,
                    kind="audit_item",
                    item_number=number,
                    file_path=stored.path,
                    original_name=stored.original_name,
                    size=stored.size,
                    content_type=stored.content_type,
                )
            )

        self.notifications.add_all(
            [
                Notification(
                    user_id=audit.expert_id,
                    expertise_id=audit.id,
                    text=f"Заказчик загрузил документы по перечню, заявка №{audit.id}",
                )
            ]
        )

        return await self.expertises.save(audit)
