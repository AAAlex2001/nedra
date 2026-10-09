"""Сценарий подачи заявки на аудит СУПБ."""

from fastapi import UploadFile

from app.models.expertise import (
    ContractKind,
    Expertise,
    ExpertiseDocument,
    ExpertiseStatus,
    ServiceKind,
)
from app.models.notification import Notification
from app.models.user import User
from app.schemas.audit import AuditInSchema
from app.schemas.audit_details import AuditDetailsSchema
from app.services.audit.checklist import AUDIT_DOCUMENTS
from app.services.audit.files import save_audit_file
from app.services.experts.repo import ExpertProfileRepository
from app.services.expertise.exceptions import InvalidExpertiseError
from app.services.expertise.repo import ExpertiseRepository
from app.services.expertise.usecases.create_expertise import (
    DOCUMENTS_FOLDER,
    CreatedExpertise,
    build_company,
)
from app.services.files.storage import PrivateStorage
from app.services.notifications.repo import NotificationRepository

OBJECT_NAME_LIMIT = 500


def describe_object(details: AuditDetailsSchema) -> str:
    """Что проверяем — одной строкой для договора, уведомлений и списка заявок."""

    if details.scope == "all" and details.fleet is not None:
        return f"Все ОПО {details.applicant.organization} ({details.fleet.count})"

    names = "; ".join(f"{item.name} ({item.reg_number})" for item in details.objects)

    return names[:OBJECT_NAME_LIMIT]


class CreateAuditUseCase:
    """Сохранить заявку на аудит с файлами и уведомить руководителей аудиторских групп.

    Документы по перечню на этапе заявки необязательны: основная загрузка
    открывается после согласования Плана аудита. Если заказчику нужна
    консультация по типу аудита, заявку сначала видит менеджер, а не аудиторы.
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
        opo_certificate: UploadFile | None = None,
        power_of_attorney: UploadFile | None = None,
        sto_file: UploadFile | None = None,
    ) -> CreatedExpertise:
        """Создать заявку. Бросает InvalidExpertiseError, InvalidCompanyError и UploadError."""

        details = data.details

        if len(files) != len(items):
            raise InvalidExpertiseError("Для каждого файла нужен номер пункта перечня")

        for number in items:
            if number < 1 or number > len(AUDIT_DOCUMENTS):
                raise InvalidExpertiseError(f"В перечне нет пункта {number}")

        if details.applicant.by_proxy and power_of_attorney is None:
            raise InvalidExpertiseError("Приложите доверенность заявителя")

        if details.params.use_sto and sto_file is None:
            raise InvalidExpertiseError("Приложите файл СТО")

        if details.params.kind == "consultation":
            status = ExpertiseStatus.CONSULTATION
            leads = []
        else:
            status = ExpertiseStatus.NEW
            leads = await self.profiles.list_audit_leads()

        audit = Expertise(
            customer_id=customer.id,
            service=ServiceKind.AUDIT,
            contract_kind=ContractKind.AUDIT,
            object_name=describe_object(details),
            comment=data.comment.strip() if data.comment else None,
            audit_details=details.model_dump(mode="json"),
            status=status,
            price=data.price,
            customer_type=data.customer_type,
            company=build_company(data.company),
        )

        for file, number in zip(files, items):
            await self.attach(audit, customer, file, "audit_item", number)

        if company_card is not None:
            await self.attach(audit, customer, company_card, "company_card")

        if opo_certificate is not None and details.scope == "all":
            await self.attach(audit, customer, opo_certificate, "opo_certificate")

        if power_of_attorney is not None and details.applicant.by_proxy:
            await self.attach(audit, customer, power_of_attorney, "power_of_attorney")

        if sto_file is not None and details.params.use_sto:
            await self.attach(audit, customer, sto_file, "sto")

        self.notifications.add_all(
            [
                Notification(
                    user_id=lead.id,
                    expertise=audit,
                    text=f"Новая заявка на аудит СУПБ: {audit.object_name}",
                )
                for lead in leads
            ]
        )

        saved = await self.expertises.add(audit)

        return CreatedExpertise(expertise=saved, notified_experts=leads)

    async def attach(
        self,
        audit: Expertise,
        customer: User,
        file: UploadFile,
        kind: str,
        number: int | None = None,
    ) -> None:
        """Сохранить файл заказчика и приложить его к заявке."""

        stored = await save_audit_file(self.storage, file, DOCUMENTS_FOLDER)
        audit.documents.append(
            ExpertiseDocument(
                uploaded_by=customer.id,
                kind=kind,
                item_number=number,
                file_path=stored.path,
                original_name=stored.original_name,
                size=stored.size,
                content_type=stored.content_type,
            )
        )
