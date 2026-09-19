"""Шаг 10: эксперт прикладывает подписанное ЭЦП заключение и отправляет заказчику."""

from datetime import datetime, timezone

from fastapi import UploadFile

from app.models.expertise import Expertise, ExpertiseDocument, ExpertiseResult, ExpertiseStatus
from app.models.notification import Notification
from app.models.user import User
from app.services.expertise.exceptions import (
    ExpertiseAccessError,
    ExpertiseStateError,
    InvalidExpertiseError,
)
from app.services.expertise.repo import ExpertiseRepository
from app.services.files.storage import CONCLUSION_TYPES, DOCUMENTATION_MAX_SIZE_BYTES, PrivateStorage
from app.services.notifications.repo import NotificationRepository

CONCLUSIONS_FOLDER = "expertise-conclusions"


class SendConclusionUseCase:
    """Сохранить файлы заключения, записать исход и перевести экспертизу в sent.

    ЭЦП ставится на стороне эксперта его средством подписи: сюда приходит
    уже подписанный PDF или файл с отсоединённой подписью (.sig, .p7s).
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
        self, expert: User, expertise: Expertise, result: str, files: list[UploadFile]
    ) -> Expertise:
        """Бросает ExpertiseStateError, ExpertiseAccessError, InvalidExpertiseError, UploadError."""

        if expertise.expert_id != expert.id:
            raise ExpertiseAccessError("Это не ваша экспертиза")

        if expertise.status != ExpertiseStatus.PAID:
            raise ExpertiseStateError("Отправить заключение можно после оплаты остатка")

        if result not in ExpertiseResult:
            raise InvalidExpertiseError("Укажите исход экспертизы: положительное, отрицательное или замечания")

        if not files:
            raise InvalidExpertiseError("Приложите файл заключения")

        for file in files:
            stored = await self.storage.save(
                file, CONCLUSIONS_FOLDER, DOCUMENTATION_MAX_SIZE_BYTES, CONCLUSION_TYPES
            )
            expertise.documents.append(
                ExpertiseDocument(
                    uploaded_by=expert.id,
                    kind="conclusion",
                    file_path=stored.path,
                    original_name=stored.original_name,
                    size=stored.size,
                    content_type=stored.content_type,
                )
            )

        expertise.result = result
        expertise.sent_at = datetime.now(timezone.utc)
        expertise.status = ExpertiseStatus.SENT

        self.notifications.add_all(
            [
                Notification(
                    user_id=expertise.customer_id,
                    expertise_id=expertise.id,
                    text=f"Заключение по заявке №{expertise.id} отправлено, его можно скачать в кабинете",
                )
            ]
        )

        return await self.expertises.save(expertise)
