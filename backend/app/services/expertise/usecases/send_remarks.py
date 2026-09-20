"""Шаг 8а: эксперт выдаёт замечания вместо готового заключения."""

from fastapi import UploadFile

from app.models.expertise import Expertise, ExpertiseDocument, ExpertiseRemark, ExpertiseStatus
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

REMARKS_FOLDER = "expertise-remarks"


class SendRemarksUseCase:
    """Сохранить рекомендации по приведению объекта в соответствие и вернуть документацию заказчику.

    Эксперт пишет текст, прикладывает файл или делает и то и другое.
    Экспертиза уходит в статус remarks и ждёт исправленную документацию.
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
        self, expert: User, expertise: Expertise, text: str | None, files: list[UploadFile]
    ) -> Expertise:
        """Бросает ExpertiseStateError, ExpertiseAccessError, InvalidExpertiseError, UploadError."""

        if expertise.expert_id != expert.id:
            raise ExpertiseAccessError("Это не ваша экспертиза")

        if expertise.status != ExpertiseStatus.IN_PROGRESS:
            raise ExpertiseStateError("Замечания выдаются, пока идёт экспертиза")

        comment = text.strip() if text else None
        if not comment and not files:
            raise InvalidExpertiseError("Напишите замечания или приложите файл")

        remark = ExpertiseRemark(text=comment)
        expertise.remarks.append(remark)

        for file in files:
            stored = await self.storage.save(file, REMARKS_FOLDER, DOCUMENTATION_MAX_SIZE_BYTES)
            document = ExpertiseDocument(
                uploaded_by=expert.id,
                kind="remarks",
                file_path=stored.path,
                original_name=stored.original_name,
                size=stored.size,
                content_type=stored.content_type,
            )
            expertise.documents.append(document)
            remark.documents.append(document)

        expertise.status = ExpertiseStatus.REMARKS

        self.notifications.add_all(
            [
                Notification(
                    user_id=expertise.customer_id,
                    expertise_id=expertise.id,
                    text=f"Эксперт прислал замечания по заявке №{expertise.id}. Исправьте документацию и отправьте повторно",
                )
            ]
        )

        return await self.expertises.save(expertise)
