"""Правка и удаление экспертизы администратором."""

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

from app.models.expertise import Expertise, ExpertiseStatus, ServiceKind
from app.models.notification import Notification
from app.models.user import User, UserRole
from app.services.contracts.kinds import resolve_kind
from app.services.experts.repo import ExpertProfileRepository
from app.services.expertise.exceptions import ExpertiseNotFoundError, InvalidExpertiseError
from app.services.expertise.repo import ExpertiseRepository
from app.services.files.storage import PrivateStorage
from app.services.notifications.repo import NotificationRepository
from app.services.users.repo import UserRepository


@dataclass(frozen=True)
class AdminUpdate:
    """Итог правки: заявка и руководители групп, которым она открылась после консультации."""

    expertise: Expertise
    released_to: list[User]


class UpdateExpertiseUseCase:
    """Поменять статус, стоимость и эксперта заявки руками, когда стороны договорились иначе.

    Назначая эксперта, админ делает то же, что эксперт кнопкой «Готов провести»:
    закрепляет заявку и, если заказчик не знал вид проекта, определяет вид договора.
    Переводя аудит из консультации в «Ждёт аудитора», админ открывает заявку
    руководителям групп — они получают уведомление.
    """

    def __init__(
        self,
        expertises: ExpertiseRepository,
        users: UserRepository,
        profiles: ExpertProfileRepository,
        notifications: NotificationRepository,
    ) -> None:
        self.expertises = expertises
        self.users = users
        self.profiles = profiles
        self.notifications = notifications

    async def execute(
        self,
        expertise_id: int,
        status: ExpertiseStatus,
        price: Decimal | None,
        expert_id: int | None,
        contract_kind: str | None,
    ) -> AdminUpdate:
        """Бросает ExpertiseNotFoundError и InvalidExpertiseError."""

        expertise = await self.expertises.get_by_id(expertise_id)
        if expertise is None:
            raise ExpertiseNotFoundError(f"Экспертиза {expertise_id} не найдена")

        released = (
            expertise.service == ServiceKind.AUDIT
            and expertise.status == ExpertiseStatus.CONSULTATION
            and status == ExpertiseStatus.NEW
            and expert_id is None
        )

        if expert_id is not None:
            expert = await self.users.get_by_id(expert_id)
            if expert is None or expert.role != UserRole.EXPERT:
                raise InvalidExpertiseError("Такого эксперта нет")

        if expert_id is not None and expertise.contract_kind is None:
            expertise.contract_kind = resolve_kind(expertise.object_code, contract_kind)

        if expert_id is not None and expertise.contract_kind is None:
            raise InvalidExpertiseError("Выберите вид договора")

        unassigned = (ExpertiseStatus.NEW, ExpertiseStatus.CONSULTATION)
        if status not in unassigned and expert_id is None:
            raise InvalidExpertiseError("Для этого статуса нужен назначенный эксперт")

        if expert_id is not None and expertise.expert_ready_at is None:
            expertise.expert_ready_at = datetime.now(timezone.utc)

        expertise.expert_id = expert_id
        expertise.status = status
        expertise.price = price

        leads = await self.profiles.list_audit_leads() if released else []
        self.notifications.add_all(
            [
                Notification(
                    user_id=lead.id,
                    expertise_id=expertise.id,
                    text=f"Новая заявка на аудит СУПБ: {expertise.object_name}",
                )
                for lead in leads
            ]
        )

        saved = await self.expertises.save(expertise)

        return AdminUpdate(expertise=saved, released_to=leads)


class DeleteExpertiseUseCase:
    """Удалить заявку вместе с файлами: документацией, замечаниями и заключением.

    Строки в базе уходят каскадом, а файлы на диске надо убрать вручную,
    иначе закрытое хранилище будет расти мусором.
    """

    def __init__(self, expertises: ExpertiseRepository, storage: PrivateStorage) -> None:
        self.expertises = expertises
        self.storage = storage

    async def execute(self, expertise_id: int) -> None:
        """Бросает ExpertiseNotFoundError."""

        expertise = await self.expertises.get_by_id(expertise_id)
        if expertise is None:
            raise ExpertiseNotFoundError(f"Экспертиза {expertise_id} не найдена")

        for document in expertise.documents:
            self.storage.remove(document.file_path)

        await self.expertises.remove(expertise)
