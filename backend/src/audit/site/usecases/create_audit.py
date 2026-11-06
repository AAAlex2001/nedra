"""Подача заявки на аудит."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.audit_letters import AuditLetters
from src.audit.enums import AuditStatus
from src.audit.exceptions import AuditAccessError
from src.audit.models.audit import Audit
from src.audit.models.audit_application import AuditApplication
from src.audit.models.audit_company import AuditCompany
from src.audit.models.audit_document import AuditDocument
from src.audit.repositories.audit_requests import AuditRequestRepository
from src.audit.site.audit_file_storage import AuditFileStorage, SavedAuditDocument
from src.audit.site.audit_upload_files import AuditUploadFiles
from src.audit.site.schemas.create_audit import CreateAuditRequest, CreateAuditResponse
from src.contracts.models.contract import Contract
from src.contracts.repositories.contracts import ContractRepository
from src.notifications.models.notification import Notification
from src.notifications.options import NOTIFICATION_TEXT_MAX_LENGTH
from src.notifications.repositories.notifications import NotificationRepository
from src.users.enums import UserRole
from src.users.models.user import User
from src.users.repositories.expert_profiles import ExpertProfileRepository


class CreateAuditUseCase:
    """Создание заявки на аудит."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        requests: AuditRequestRepository,
        contracts: ContractRepository,
        profiles: ExpertProfileRepository,
        notifications: NotificationRepository,
        files: AuditFileStorage,
        letters: AuditLetters,
    ) -> None:
        """Заявки, уведомления и файлы."""

        self.session = session
        self.requests = requests
        self.contracts = contracts
        self.profiles = profiles
        self.notifications = notifications
        self.files = files
        self.letters = letters

    async def execute(
        self,
        *,
        user: User,
        payload: CreateAuditRequest,
        files: AuditUploadFiles,
    ) -> CreateAuditResponse:
        """Подать заявку на аудит."""

        if user.role != UserRole.CUSTOMER:
            raise AuditAccessError("Заявку подаёт заказчик")

        attachments = files.prepare_attachments(details=payload.details)
        object_name = payload.describe_objects()
        status = AuditStatus.NEW
        audit_leads = []

        if payload.details.params.kind == "consultation":
            status = AuditStatus.CONSULTATION
        else:
            audit_leads = await self.profiles.list_audit_leads()

        documents = []

        try:
            documents = await self.files.save_all(attachments=attachments)
            created_audit = await self._save_request(
                customer_id=user.id,
                payload=payload,
                status=status,
                object_name=object_name,
                documents=documents,
            )
            await self.contracts.save(
                contract=Contract(
                    audit_id=created_audit.id,
                    kind="audit",
                ),
            )
            await self.notifications.add_many(
                notifications=[
                    Notification(
                        user_id=lead.id,
                        audit_id=created_audit.id,
                        text=f"Новая заявка на аудит СУПБ: {object_name}"[
                            :NOTIFICATION_TEXT_MAX_LENGTH
                        ],
                    )
                    for lead in audit_leads
                ]
            )
            response = CreateAuditResponse.from_model(audit=created_audit)
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

        if status == AuditStatus.CONSULTATION:
            await self.letters.send_consultation_request(
                audit_id=response.id,
                object_name=object_name,
                applicant=payload.details.applicant,
            )
        else:
            await self.letters.send_new_application(
                audit_id=response.id,
                object_name=object_name,
                recipients=[lead.email for lead in audit_leads],
            )

        return response

    async def _save_request(
        self,
        *,
        customer_id: int,
        payload: CreateAuditRequest,
        status: AuditStatus,
        object_name: str,
        documents: list[SavedAuditDocument],
    ) -> Audit:
        """Добавить заявку с реквизитами и документами."""

        audit = Audit(
            customer_id=customer_id,
            customer_type=payload.customer_type,
            comment=payload.comment,
            status=status,
            customer_budget=payload.price,
            negotiation_allowed=payload.details.budget.negotiation != "no",
        )

        application = AuditApplication(
            object_name=object_name,
            details=payload.details.model_dump(mode="json"),
        )
        company = AuditCompany(
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
                AuditDocument(
                    uploaded_by=customer_id,
                    kind=document.kind,
                    item_number=document.item_number,
                    file_path=document.file.path,
                    original_name=document.file.original_name,
                    size=document.file.size,
                    content_type=document.file.content_type,
                )
            )

        await self.requests.add(
            audit=audit,
            application=application,
            company=company,
            documents=document_records,
        )

        return audit
