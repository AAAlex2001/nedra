"""Шаг 5–6: заказчик соглашается с договором и соглашением о конфиденциальности."""

from datetime import datetime, timezone

from app.models.expertise import Expertise, ExpertiseDocument, ExpertiseStatus
from app.models.notification import Notification
from app.models.user import User
from app.services.contracts.document import (
    CONTRACT,
    DOCX_TYPE,
    NDA,
    build_signed_document,
    contract_problem,
    signed_filename,
)
from app.services.contracts.executors import executor_for, executor_requisites
from app.services.expertise.exceptions import ExpertiseAccessError, ExpertiseStateError
from app.services.expertise.repo import ExpertiseRepository
from app.services.files.storage import PrivateStorage
from app.services.notifications.repo import NotificationRepository

DOCUMENTS_FOLDER = "expertise-documents"


class ConfirmExpertiseUseCase:
    """Вторая подпись: заказчик согласен с договором, можно платить аванс.

    Договор и соглашение о конфиденциальности собираются из шаблонов
    исполнителя в момент согласия и хранятся в заявке файлами: если потом
    поменяются шаблоны или реквизиты, у сторон останется ровно тот текст,
    с которым заказчик согласился.
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

    async def execute(self, customer: User, expertise: Expertise) -> Expertise:
        """Перевести заявку в contract.

        Бросает ExpertiseStateError, ExpertiseAccessError и CompanyRequisitesMissingError.
        """

        if expertise.customer_id != customer.id:
            raise ExpertiseAccessError("Подтвердить может только заказчик этой заявки")

        if expertise.status != ExpertiseStatus.EXPERT_READY or expertise.expert_id is None:
            raise ExpertiseStateError("Эксперт ещё не подтвердил готовность")

        problem = contract_problem(expertise)
        if problem is not None:
            raise ExpertiseStateError(problem)

        signed_at = datetime.now(timezone.utc)
        requisites = executor_requisites(executor_for(expertise.contract_kind))

        for kind in (CONTRACT, NDA):
            content = build_signed_document(
                kind, expertise, customer, requisites.vat_rate, signed_at
            )
            stored = self.storage.save_bytes(
                content,
                DOCUMENTS_FOLDER,
                signed_filename(kind, expertise, signed_at),
                DOCX_TYPE,
                ".docx",
            )
            expertise.documents.append(
                ExpertiseDocument(
                    uploaded_by=customer.id,
                    kind=kind,
                    file_path=stored.path,
                    original_name=stored.original_name,
                    size=stored.size,
                    content_type=stored.content_type,
                )
            )

        expertise.contract_at = signed_at
        expertise.status = ExpertiseStatus.CONTRACT

        self.notifications.add_all(
            [
                Notification(
                    user_id=expertise.expert_id,
                    expertise_id=expertise.id,
                    text=f"Заказчик подписал договор и соглашение о конфиденциальности по заявке №{expertise.id}, ждём аванс",
                )
            ]
        )

        return await self.expertises.save(expertise)
