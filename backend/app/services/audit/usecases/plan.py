"""Этап «Согласование Программы и Плана аудита».

После аванса руководитель группы заполняет План и отправляет его заказчику.
Заказчик согласует План или просит скорректировать: тогда руководитель
вносит изменения и отправляет новую версию. Согласованный План открывает
загрузку и проверку документов.
"""

from datetime import datetime, timezone

from app.models.expertise import Expertise, ExpertiseDocument, ExpertiseStatus, ServiceKind
from app.models.notification import Notification
from app.models.user import User
from app.schemas.audit_details import AuditDetailsSchema, AuditPlanInSchema, AuditPlanSchema
from app.services.audit.plan_document import build_plan_document, plan_filename
from app.services.audit.team import TeamMember
from app.services.contracts.document import DOCX_TYPE
from app.services.expertise.exceptions import (
    ExpertiseAccessError,
    ExpertiseStateError,
    InvalidExpertiseError,
)
from app.services.expertise.repo import ExpertiseRepository
from app.services.files.storage import PrivateStorage
from app.services.notifications.repo import NotificationRepository

PLANS_FOLDER = "audit-plans"
PLAN_DOCUMENT = "audit_plan"


def team_ids(audit: Expertise) -> list[int]:
    """Все аудиторы группы вместе с руководителем."""

    lead = [audit.expert_id] if audit.expert_id is not None else []

    return lead + [member.user_id for member in audit.team]


class SendPlanUseCase:
    """Руководитель группы отправляет заказчику новую версию Плана аудита."""

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
        self,
        lead: User,
        audit: Expertise,
        data: AuditPlanInSchema,
        team: list[TeamMember],
    ) -> Expertise:
        """Бросает ExpertiseAccessError, ExpertiseStateError, InvalidExpertiseError."""

        if audit.service != ServiceKind.AUDIT or audit.audit_details is None:
            raise InvalidExpertiseError("План составляется только по заявке на аудит")

        if audit.expert_id != lead.id:
            raise ExpertiseAccessError("План отправляет руководитель аудиторской группы")

        if audit.status != ExpertiseStatus.PLAN:
            raise ExpertiseStateError("Сейчас План аудита не ожидается")

        details = AuditDetailsSchema.model_validate(audit.audit_details)

        if "onsite" in details.stages and data.onsite_start is None:
            raise InvalidExpertiseError("Заказчик выбрал выездной этап: укажите его даты")

        version = (audit.audit_plan or {}).get("version", 0) + 1
        plan = AuditPlanSchema(**data.model_dump(), version=version)
        now = datetime.now(timezone.utc)

        content = build_plan_document(audit, details, plan, team, now)
        stored = self.storage.save_bytes(
            content, PLANS_FOLDER, plan_filename(audit, version), DOCX_TYPE, ".docx"
        )
        audit.documents.append(
            ExpertiseDocument(
                uploaded_by=lead.id,
                kind=PLAN_DOCUMENT,
                file_path=stored.path,
                original_name=stored.original_name,
                size=stored.size,
                content_type=stored.content_type,
            )
        )

        audit.audit_plan = plan.model_dump(mode="json")
        audit.plan_comment = None
        audit.plan_sent_at = now
        audit.status = ExpertiseStatus.PLAN_REVIEW

        self.notifications.add_all(
            [
                Notification(
                    user_id=audit.customer_id,
                    expertise_id=audit.id,
                    text=f"План аудита по заявке №{audit.id} ждёт вашего согласования",
                )
            ]
        )

        return await self.expertises.save(audit)


class ApprovePlanUseCase:
    """Заказчик согласует План: открывается загрузка и проверка документов."""

    def __init__(
        self, expertises: ExpertiseRepository, notifications: NotificationRepository
    ) -> None:
        self.expertises = expertises
        self.notifications = notifications

    async def execute(self, customer: User, audit: Expertise) -> Expertise:
        """Бросает ExpertiseAccessError и ExpertiseStateError."""

        if audit.customer_id != customer.id:
            raise ExpertiseAccessError("Согласовать План может только заказчик этой заявки")

        if audit.status != ExpertiseStatus.PLAN_REVIEW:
            raise ExpertiseStateError("План аудита сейчас не ждёт согласования")

        audit.plan_approved_at = datetime.now(timezone.utc)
        audit.status = ExpertiseStatus.IN_PROGRESS

        self.notifications.add_all(
            [
                Notification(
                    user_id=user_id,
                    expertise_id=audit.id,
                    text=f"Заказчик согласовал План аудита по заявке №{audit.id}, "
                    "документы открыты для проверки",
                )
                for user_id in team_ids(audit)
            ]
        )

        return await self.expertises.save(audit)


class RequestPlanChangesUseCase:
    """Заказчик просит скорректировать План: руководитель группы получает комментарий."""

    def __init__(
        self, expertises: ExpertiseRepository, notifications: NotificationRepository
    ) -> None:
        self.expertises = expertises
        self.notifications = notifications

    async def execute(self, customer: User, audit: Expertise, comment: str) -> Expertise:
        """Бросает ExpertiseAccessError и ExpertiseStateError."""

        if audit.customer_id != customer.id:
            raise ExpertiseAccessError("Запросить корректировки может только заказчик этой заявки")

        if audit.status != ExpertiseStatus.PLAN_REVIEW or audit.expert_id is None:
            raise ExpertiseStateError("План аудита сейчас не ждёт согласования")

        audit.plan_comment = comment.strip()
        audit.status = ExpertiseStatus.PLAN

        self.notifications.add_all(
            [
                Notification(
                    user_id=audit.expert_id,
                    expertise_id=audit.id,
                    text=f"Заказчик просит скорректировать План аудита по заявке №{audit.id}",
                )
            ]
        )

        return await self.expertises.save(audit)
