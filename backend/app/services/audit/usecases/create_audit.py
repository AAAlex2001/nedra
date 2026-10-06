"""Сценарий подачи заявки на аудит СУПБ."""

from fastapi import UploadFile

from app.models.expertise import (
    ContractKind,
    CustomerType,
    Expertise,
    ExpertiseDocument,
    ExpertiseStatus,
    ServiceKind,
)
from app.models.notification import Notification
from app.models.user import User
from app.schemas.audit import AuditInSchema
from app.services.audit.checklist import AUDIT_DOCUMENTS
from app.services.experts.repo import ExpertProfileRepository
from app.services.expertise.exceptions import InvalidExpertiseError
from app.services.expertise.repo import ExpertiseRepository
from app.services.expertise.usecases.create_expertise import (
    DOCUMENTS_FOLDER,
    CreatedExpertise,
    build_company,
    build_individual,
)
from app.services.files.storage import DOCUMENTATION_MAX_SIZE_BYTES, PrivateStorage
from app.services.notifications.repo import NotificationRepository


class CreateAuditUseCase:
    """Сохранить заявку на аудит с документами по перечню и уведомить аудиторов.

    Заказчик может загрузить не все документы: недостающие видно в отчёте
    о представленных документах, который собирается в кабинете аудитора.
    """

    def __init__(
        self,
        expertises: ExpertiseRepository,
        profiles: ExpertProfileRepository,
        notifications: NotificationRepository,
        storage: PrivateStorage,
    ) -> None:
        self.expertises = expertises
        self.profiles = profiles
        self.notifications = notifications
        self.storage = storage

    async def execute(
        self,
        customer: User,
        data: AuditInSchema,
        files: list[UploadFile],
        items: list[int],
        company_card: UploadFile | None = None,
    ) -> CreatedExpertise:
        """Создать заявку. Бросает InvalidExpertiseError, InvalidCompanyError и UploadError."""

        if not files:
            raise InvalidExpertiseError("Загрузите хотя бы один документ по перечню")

        if len(files) != len(items):
            raise InvalidExpertiseError("Для каждого файла нужен номер пункта перечня")

        for number in items:
            if number < 1 or number > len(AUDIT_DOCUMENTS):
                raise InvalidExpertiseError(f"В перечне нет пункта {number}")

        company = None
        individual = None
        if data.customer_type == CustomerType.LEGAL and data.company is not None:
            company = build_company(data.company)
        if data.customer_type == CustomerType.INDIVIDUAL and data.individual is not None:
            individual = build_individual(data.individual)

        audit = Expertise(
            customer_id=customer.id,
            service=ServiceKind.AUDIT,
            contract_kind=ContractKind.AUDIT,
            deadline=data.deadline,
            object_name=data.object_name.strip(),
            comment=data.comment.strip() if data.comment else None,
            status=ExpertiseStatus.NEW,
            price=data.price,
            customer_type=data.customer_type,
            company=company,
            individual=individual,
        )

        for file, number in zip(files, items):
            stored = await self.storage.save(file, DOCUMENTS_FOLDER, DOCUMENTATION_MAX_SIZE_BYTES)
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

        if company_card is not None:
            stored = await self.storage.save(
                company_card, DOCUMENTS_FOLDER, DOCUMENTATION_MAX_SIZE_BYTES
            )
            audit.documents.append(
                ExpertiseDocument(
                    uploaded_by=customer.id,
                    kind="company_card",
                    file_path=stored.path,
                    original_name=stored.original_name,
                    size=stored.size,
                    content_type=stored.content_type,
                )
            )

        auditors = await self.profiles.list_auditors()

        notifications = [
            Notification(
                user_id=auditor.id,
                expertise=audit,
                text=f"Новая заявка на аудит СУПБ: {audit.object_name}",
            )
            for auditor in auditors
        ]
        self.notifications.add_all(notifications)

        saved = await self.expertises.add(audit)

        return CreatedExpertise(expertise=saved, notified_experts=auditors)
