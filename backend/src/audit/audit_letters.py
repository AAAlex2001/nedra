"""Письма об аудите."""

from datetime import UTC, datetime

from src.audit.options import AUDIT_INVITATION_CONTENT_TYPE, AUDIT_INVITATION_FILENAME
from src.audit.schemas.audit_details import AuditApplicantSchema
from src.audit.site.documents.meeting_invitation import create_meeting_invitation
from src.audit.site.schemas.audit_plan import AuditPlanResponse
from src.core.email_sender import EmailAttachment, EmailSender
from src.documents.text_formatting import format_moscow_time


class AuditLetters:
    """Почтовые уведомления участников аудита."""

    def __init__(
        self,
        *,
        sender: EmailSender,
        cabinet_url: str,
        manager_emails: list[str],
    ) -> None:
        """Отправитель и адреса получателей."""

        self.sender = sender
        self.cabinet_url = cabinet_url
        self.manager_emails = manager_emails

    async def send_new_application(
        self,
        *,
        audit_id: int,
        object_name: str,
        recipients: list[str],
    ) -> None:
        """Сообщить аудиторам о новой заявке."""

        for recipient in recipients:
            await self.sender.send(
                recipient=recipient,
                subject=f"Новая заявка на аудит №{audit_id}",
                text=f"Аудит СУПБ: {object_name}\n\nЗаявка в личном кабинете: {self.cabinet_url}",
            )

    async def send_consultation_request(
        self,
        *,
        audit_id: int,
        object_name: str,
        applicant: AuditApplicantSchema,
    ) -> None:
        """Сообщить менеджерам о запросе консультации."""

        for recipient in self.manager_emails:
            await self.sender.send(
                recipient=recipient,
                subject=f"Консультация по аудиту №{audit_id}",
                text=(
                    f"Заказчик просит помочь выбрать вид аудита: {object_name}\n"
                    f"Представитель: {applicant.full_name}, {applicant.position}\n"
                    f"Организация: {applicant.organization}, ИНН {applicant.inn}\n"
                    f"Телефон: {applicant.phone}\nПочта: {applicant.email}\n\n"
                    f"Заявка в личном кабинете: {self.cabinet_url}"
                ),
            )

    async def send_price_update(
        self,
        *,
        audit_id: int,
        recipient: str,
        text: str,
    ) -> None:
        """Сообщить об обсуждении цены."""

        await self.sender.send(
            recipient=recipient,
            subject=f"Стоимость аудита №{audit_id}",
            text=f"{text}\n\nЗаявка в личном кабинете: {self.cabinet_url}",
        )

    async def send_plan_submitted(
        self,
        *,
        audit_id: int,
        recipient: str,
    ) -> None:
        """Сообщить о готовом плане аудита."""

        await self.sender.send(
            recipient=recipient,
            subject=f"План аудита №{audit_id} ждёт согласования",
            text=(
                "Руководитель группы подготовил план аудита. "
                "Ознакомьтесь с ним и согласуйте или запросите изменения.\n\n"
                f"Заявка в личном кабинете: {self.cabinet_url}"
            ),
        )

    async def send_plan_changes(
        self,
        *,
        audit_id: int,
        recipient: str,
        comment: str,
    ) -> None:
        """Сообщить о замечаниях к плану."""

        await self.sender.send(
            recipient=recipient,
            subject=f"Корректировки плана аудита №{audit_id}",
            text=(
                f"Заказчик просит изменить план аудита:\n{comment}\n\n"
                f"Заявка в личном кабинете: {self.cabinet_url}"
            ),
        )

    async def send_plan_approved(
        self,
        *,
        audit_id: int,
        object_name: str | None,
        plan: AuditPlanResponse,
        recipients: list[str],
    ) -> None:
        """Сообщить о согласовании и приложить приглашение."""

        invitation = create_meeting_invitation(
            audit_id=audit_id,
            object_name=object_name,
            plan=plan,
            generated_at=datetime.now(UTC),
        )
        attachments = []
        meeting_text = ""

        if invitation is not None and plan.opening_at is not None:
            attachments.append(
                EmailAttachment(
                    filename=AUDIT_INVITATION_FILENAME,
                    content=invitation,
                    content_type=AUDIT_INVITATION_CONTENT_TYPE,
                )
            )
            meeting_text = (
                f"\nВступительное совещание: {format_moscow_time(moment=plan.opening_at)}."
            )

            if plan.meeting_link:
                meeting_text += f"\nСсылка для подключения: {plan.meeting_link}"

        for recipient in recipients:
            await self.sender.send(
                recipient=recipient,
                subject=f"План аудита №{audit_id} согласован",
                text=(
                    "План согласован заказчиком. Открыта загрузка и проверка документов."
                    f"{meeting_text}\n\nЗаявка в личном кабинете: {self.cabinet_url}"
                ),
                attachments=attachments,
            )
