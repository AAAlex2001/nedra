"""Подача документации на экспертизу."""

from fastapi import UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.contracts.enums import CustomerType
from src.contracts.models.contract import Contract
from src.contracts.repositories.contracts import ContractRepository
from src.expertise.application_validation import (
    determine_contract_kind,
    determine_expert_category,
    validate_expertise_codes,
)
from src.expertise.exceptions import ExpertiseAccessError, InvalidExpertiseError
from src.expertise.models.expertise import Expertise
from src.expertise.models.expertise_company import ExpertiseCompany
from src.expertise.models.expertise_document import ExpertiseDocument
from src.expertise.models.expertise_individual import ExpertiseIndividual
from src.expertise.repositories.expertise_requests import ExpertiseRequestRepository
from src.expertise.repositories.qualified_experts import QualifiedExpertRepository
from src.expertise.site.expertise_file_storage import (
    ExpertiseAttachment,
    ExpertiseFileStorage,
    SavedExpertiseDocument,
)
from src.expertise.site.expertise_letters import ExpertiseLetters
from src.expertise.site.schemas.create_expertise import (
    CreateExpertiseRequest,
    CreateExpertiseResponse,
)
from src.notifications.models.notification import Notification
from src.notifications.repositories.notifications import NotificationRepository
from src.users.enums import UserRole
from src.users.models.user import User


class CreateExpertiseUseCase:
    """Новая заявка на экспертизу."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        requests: ExpertiseRequestRepository,
        contracts: ContractRepository,
        experts: QualifiedExpertRepository,
        notifications: NotificationRepository,
        files: ExpertiseFileStorage,
        letters: ExpertiseLetters,
    ) -> None:
        """Заявки, исполнители и документы."""

        self.session = session
        self.requests = requests
        self.contracts = contracts
        self.experts = experts
        self.notifications = notifications
        self.files = files
        self.letters = letters

    async def execute(
        self,
        *,
        user: User,
        payload: CreateExpertiseRequest,
        files: list[UploadFile],
        company_card: UploadFile | None,
    ) -> CreateExpertiseResponse:
        """Подать заявку на экспертизу."""

        if user.role != UserRole.CUSTOMER:
            raise ExpertiseAccessError("Заявку подаёт заказчик")

        validate_expertise_codes(
            object_code=payload.object_code,
            area_code=payload.area_code,
        )
        category = determine_expert_category(
            hazard_class=payload.hazard_class,
            expert_category=payload.expert_category,
        )
        contract_kind = determine_contract_kind(
            object_code=payload.object_code,
            chosen_kind=payload.contract_kind,
        )

        if not files:
            raise InvalidExpertiseError("Приложите хотя бы один файл документации")

        attachments = [
            ExpertiseAttachment(
                file=file,
                kind="documentation",
            )
            for file in files
        ]

        if company_card is not None:
            attachments.append(
                ExpertiseAttachment(
                    file=company_card,
                    kind="company_card",
                )
            )

        experts = await self.experts.list_for_expertise(
            object_code=payload.object_code,
            area_code=payload.area_code,
            expert_category=category,
        )
        documents = await self.files.save_all(
            attachments=attachments,
        )

        try:
            expertise = await self._save_request(
                customer_id=user.id,
                payload=payload,
                expert_category=category,
                documents=documents,
            )
            await self.contracts.save(
                contract=Contract(
                    expertise_id=expertise.id,
                    kind=contract_kind,
                ),
            )
            notifications = [
                Notification(
                    user_id=expert.id,
                    expertise_id=expertise.id,
                    text=f"Новая заявка на экспертизу №{expertise.id}",
                )
                for expert in experts
            ]
            await self.notifications.add_many(notifications=notifications)
            response = CreateExpertiseResponse.from_model(expertise=expertise)
        except Exception:
            try:
                await self.session.rollback()
            finally:
                await self.files.remove_all(documents=documents)

            raise

        try:
            await self.session.commit()
        except IntegrityError:
            try:
                await self.session.rollback()
            finally:
                await self.files.remove_all(documents=documents)

            raise

        await self.letters.send_new_request(
            expertise_id=response.id,
            object_name=payload.object_name,
            recipients=[expert.email for expert in experts],
        )

        return response

    async def _save_request(
        self,
        *,
        customer_id: int,
        payload: CreateExpertiseRequest,
        expert_category: int | None,
        documents: list[SavedExpertiseDocument],
    ) -> Expertise:
        """Добавить заявку с реквизитами и документами."""

        expertise = Expertise(
            customer_id=customer_id,
            customer_type=payload.customer_type,
            comment=payload.comment,
            object_name=payload.object_name,
            object_code=payload.object_code,
            area_code=payload.area_code,
            hazard_class=payload.hazard_class,
            expert_category=expert_category,
            deadline=payload.deadline,
            price=payload.price,
        )

        individual = None
        company = None

        if payload.customer_type == CustomerType.INDIVIDUAL and payload.individual is not None:
            individual = ExpertiseIndividual(
                full_name=payload.individual.full_name,
                passport_number=payload.individual.passport_number,
                passport_issued_by=payload.individual.passport_issued_by,
                passport_issued_at=payload.individual.passport_issued_at,
                address=payload.individual.address,
            )
        elif payload.company is not None:
            company = ExpertiseCompany(
                full_name=payload.company.full_name,
                name=payload.company.name,
                inn=payload.company.inn,
                kpp=payload.company.kpp,
                ogrn=payload.company.ogrn,
                address=payload.company.address,
                bank=payload.company.bank,
                bic=payload.company.bic,
                account=payload.company.account,
                corr_account=payload.company.corr_account,
                signer_position=payload.company.signer_position,
                signer_name=payload.company.signer_name,
                signer_genitive=payload.company.signer_genitive,
                signer_basis=payload.company.signer_basis,
            )

        document_records = []

        for document in documents:
            document_records.append(
                ExpertiseDocument(
                    uploaded_by=customer_id,
                    kind=document.kind,
                    file_path=document.file.path,
                    original_name=document.file.original_name,
                    size=document.file.size,
                    content_type=document.file.content_type,
                )
            )

        await self.requests.add(
            expertise=expertise,
            company=company,
            individual=individual,
            documents=document_records,
        )

        return expertise
