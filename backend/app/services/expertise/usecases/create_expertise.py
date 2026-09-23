"""Сценарий подачи документации на экспертизу."""

from dataclasses import dataclass

from fastapi import UploadFile

from app.models.expertise import Expertise, ExpertiseDocument, ExpertiseStatus
from app.models.notification import Notification
from app.models.user import User
from app.schemas.expertise import ExpertiseInSchema
from app.services.experts.repo import ExpertProfileRepository
from app.services.expertise.exceptions import InvalidExpertiseError
from app.services.expertise.repo import ExpertiseRepository
from app.services.expertise.validators import resolve_category, validate_pair
from app.services.files.storage import DOCUMENTATION_MAX_SIZE_BYTES, PrivateStorage
from app.services.notifications.repo import NotificationRepository
from app.services.tariffs.repo import TariffRepository

DOCUMENTS_FOLDER = "expertise-documents"


@dataclass(frozen=True)
class CreatedExpertise:
    """Результат сценария: сама заявка и эксперты, которым ушли уведомления."""

    expertise: Expertise
    notified_experts: list[User]


class CreateExpertiseUseCase:
    """Проверить заявку по справочнику, сохранить файлы, найти подходящих экспертов и уведомить их.

    Цена фиксируется из тарифа при подаче: если админ позже поменяет тариф,
    уже поданные заявки останутся с прежней ценой. Когда заказчик не знает
    область аттестации, тариф определить нечем и цена остаётся пустой до
    уточнения.
    """

    def __init__(
        self,
        expertises: ExpertiseRepository,
        profiles: ExpertProfileRepository,
        notifications: NotificationRepository,
        tariffs: TariffRepository,
        storage: PrivateStorage,
    ) -> None:
        self.expertises = expertises
        self.profiles = profiles
        self.notifications = notifications
        self.tariffs = tariffs
        self.storage = storage

    async def execute(
        self,
        customer: User,
        data: ExpertiseInSchema,
        files: list[UploadFile],
        company_card: UploadFile | None = None,
    ) -> CreatedExpertise:
        """Создать экспертизу. Бросает InvalidExpertiseError и UploadError."""

        validate_pair(data.object_code, data.area_code)
        category = resolve_category(data.hazard_class, data.expert_category)

        if not files:
            raise InvalidExpertiseError("Приложите хотя бы один файл документации")

        price = None
        if data.object_code is not None and data.area_code is not None:
            tariff = await self.tariffs.get(data.area_code, data.object_code)
            price = tariff.price if tariff else None

        expertise = Expertise(
            customer_id=customer.id,
            object_code=data.object_code,
            area_code=data.area_code,
            hazard_class=data.hazard_class,
            expert_category=category,
            deadline=data.deadline,
            comment=data.comment.strip() if data.comment else None,
            status=ExpertiseStatus.NEW,
            price=price,
        )

        for file in files:
            stored = await self.storage.save(file, DOCUMENTS_FOLDER, DOCUMENTATION_MAX_SIZE_BYTES)
            expertise.documents.append(
                ExpertiseDocument(
                    uploaded_by=customer.id,
                    kind="documentation",
                    file_path=stored.path,
                    original_name=stored.original_name,
                    size=stored.size,
                    content_type=stored.content_type,
                )
            )

        if company_card is not None:
            stored = await self.storage.save(
                company_card, DOCUMENTS_FOLDER, DOCUMENTATION_MAX_SIZE_BYTES
            )
            expertise.documents.append(
                ExpertiseDocument(
                    uploaded_by=customer.id,
                    kind="company_card",
                    file_path=stored.path,
                    original_name=stored.original_name,
                    size=stored.size,
                    content_type=stored.content_type,
                )
            )

        experts = await self.profiles.list_certified(
            data.object_code, data.area_code, category
        )

        notifications = [
            Notification(
                user_id=expert.id,
                expertise=expertise,
                text=notification_text(data.area_code),
            )
            for expert in experts
        ]
        self.notifications.add_all(notifications)

        saved = await self.expertises.add(expertise)

        return CreatedExpertise(expertise=saved, notified_experts=experts)


def notification_text(area_code: str | None) -> str:
    """Текст уведомления эксперту: с областью, если заказчик её указал."""

    if area_code is None:
        return "Новая заявка на экспертизу, область аттестации заказчик не указал"

    return f"Новая заявка на экспертизу по вашей области {area_code}"
