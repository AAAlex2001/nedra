"""Подача заявки на аудит."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.audit_letters import AuditLetters
from src.audit.enums import AuditStatus
from src.audit.exceptions import AuditAccessError
from src.audit.repositories.audit_requests import AuditRequestRepository
from src.audit.schemas.audit import AuditResponse
from src.audit.site.audit_file_storage import AuditFileStorage
from src.audit.site.audit_object_name import describe_audit_objects
from src.audit.site.audit_upload_files import AuditUploadFiles, prepare_audit_uploads
from src.audit.site.schemas.create_audit import CreateAuditRequest
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
    ) -> AuditResponse:
        """Подать заявку на аудит."""

        if user.role != UserRole.CUSTOMER:
            raise AuditAccessError("Заявку подаёт заказчик")

        attachments = prepare_audit_uploads(
            details=payload.details,
            files=files,
        )
        object_name = describe_audit_objects(details=payload.details)
        status = AuditStatus.NEW
        audit_leads = []

        if payload.details.params.kind == "consultation":
            status = AuditStatus.CONSULTATION
        else:
            audit_leads = await self.profiles.list_audit_leads()

        documents = []

        try:
            documents = await self.files.save_all(attachments=attachments)
            created_audit = await self.requests.create(
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
            response = AuditResponse.from_model(audit=created_audit)
        except Exception:
            try:
                await self.session.rollback()
            finally:
                await self.files.remove_all(documents=documents)

            raise

        await self.session.commit()

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
