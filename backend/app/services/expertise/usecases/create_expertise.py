"""Сценарий подачи документации на экспертизу."""

from dataclasses import dataclass

from fastapi import UploadFile

from app.models.expertise import (
    CustomerType,
    Expertise,
    ExpertiseCompany,
    ExpertiseDocument,
    ExpertiseIndividual,
    ExpertiseStatus,
)
from app.models.notification import Notification
from app.models.user import User
from app.schemas.expertise import (
    ExpertiseCompanyInSchema,
    ExpertiseInSchema,
    ExpertiseIndividualInSchema,
)
from app.services.billing.validators import (
    normalize_account,
    normalize_bic,
    normalize_inn,
    normalize_kpp,
    normalize_ogrn,
)
from app.services.contracts.kinds import resolve_kind
from app.services.experts.repo import ExpertProfileRepository
from app.services.expertise.exceptions import InvalidExpertiseError
from app.services.expertise.repo import ExpertiseRepository
from app.services.expertise.validators import resolve_category, validate_pair
from app.services.files.storage import DOCUMENTATION_MAX_SIZE_BYTES, PrivateStorage
from app.services.notifications.repo import NotificationRepository

DOCUMENTS_FOLDER = "expertise-documents"
PASSPORT_DIGITS = 10


@dataclass(frozen=True)
class CreatedExpertise:
    """Результат сценария: сама заявка и эксперты, которым ушли уведомления."""

    expertise: Expertise
    notified_experts: list[User]


class CreateExpertiseUseCase:
    """Проверить заявку по справочнику, сохранить файлы, найти подходящих экспертов и уведомить их.

    Цену назначает заказчик. Эксперт видит её во входящих и берёт заявку,
    только если согласен: так цена сразу становится ценой договора.
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
        data: ExpertiseInSchema,
        files: list[UploadFile],
        company_card: UploadFile | None = None,
    ) -> CreatedExpertise:
        """Создать экспертизу. Бросает InvalidExpertiseError, InvalidCompanyError и UploadError."""

        validate_pair(data.object_code, data.area_code)
        category = resolve_category(data.hazard_class, data.expert_category)
        contract_kind = resolve_kind(data.object_code, data.contract_kind)

        company = None
        individual = None
        if data.customer_type == CustomerType.LEGAL and data.company is not None:
            company = build_company(data.company)
        if data.customer_type == CustomerType.INDIVIDUAL and data.individual is not None:
            individual = build_individual(data.individual)

        if not files:
            raise InvalidExpertiseError("Приложите хотя бы один файл документации")

        expertise = Expertise(
            customer_id=customer.id,
            object_code=data.object_code,
            area_code=data.area_code,
            hazard_class=data.hazard_class,
            expert_category=category,
            deadline=data.deadline,
            object_name=data.object_name.strip(),
            contract_kind=contract_kind,
            comment=data.comment.strip() if data.comment else None,
            status=ExpertiseStatus.NEW,
            price=data.price,
            customer_type=data.customer_type,
            company=company,
            individual=individual,
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


def build_company(data: ExpertiseCompanyInSchema) -> ExpertiseCompany:
    """Реквизиты заказчика для заявки: цифровые поля без пробелов и с проверкой длины."""

    return ExpertiseCompany(
        full_name=data.full_name.strip(),
        name=data.name.strip(),
        inn=normalize_inn(data.inn),
        kpp=normalize_kpp(data.kpp),
        ogrn=normalize_ogrn(data.ogrn),
        address=data.address.strip(),
        bank=data.bank.strip(),
        bic=normalize_bic(data.bic),
        account=normalize_account(data.account, "Расчётный счёт"),
        corr_account=normalize_account(data.corr_account, "Корреспондентский счёт"),
        signer_position=data.signer_position.strip(),
        signer_name=data.signer_name.strip(),
        signer_genitive=data.signer_genitive.strip(),
        signer_basis=data.signer_basis.strip(),
    )


def build_individual(data: ExpertiseIndividualInSchema) -> ExpertiseIndividual:
    """Данные физлица для заявки: паспорт — только цифры, серия отделена пробелом."""

    digits = "".join(char for char in data.passport_number if char.isdigit())
    if len(digits) != PASSPORT_DIGITS:
        raise InvalidExpertiseError("Серия и номер паспорта — 10 цифр")

    return ExpertiseIndividual(
        full_name=data.full_name.strip(),
        passport_number=f"{digits[:4]} {digits[4:]}",
        passport_issued_by=data.passport_issued_by.strip(),
        passport_issued_at=data.passport_issued_at,
        address=data.address.strip(),
    )


def notification_text(area_code: str | None) -> str:
    """Текст уведомления эксперту: с областью, если заказчик её указал."""

    if area_code is None:
        return "Новая заявка на экспертизу, область аттестации заказчик не указал"

    return f"Новая заявка на экспертизу по вашей области {area_code}"
