"""Ответ по заявке для кабинета с учётом того, кто на неё смотрит."""

from app.models.billing import Invoice
from app.models.expertise import Expertise, ServiceKind
from app.models.user import User, UserRole
from app.schemas.audit_details import AuditDetailsSchema, AuditPlanSchema, AuditTeamMemberSchema
from app.schemas.expertise import (
    ExpertiseCompanySchema,
    ExpertiseIndividualSchema,
    ExpertiseInvoiceSchema,
    ExpertiseOutSchema,
    ExpertisePaymentSchema,
)
from app.services.audit.team import load_team
from app.services.documents.invoice_pdf import invoice_number
from app.services.experts.repo import ExpertProfileRepository
from app.services.payments.repo import PaymentRepository
from app.services.users.repo import UserRepository


def pending_invoice(expertise: Expertise) -> Invoice | None:
    """Последний неоплаченный счёт заявки: по нему заказчик сообщает об оплате."""

    unpaid = [item for item in expertise.invoices if item.paid_at is None]

    return unpaid[-1] if unpaid else None


def to_invoice_schema(invoice: Invoice) -> ExpertiseInvoiceSchema:
    """Счёт для карточки заявки вместе с человеческим номером."""

    return ExpertiseInvoiceSchema(
        id=invoice.id,
        number=invoice_number(invoice),
        amount=invoice.amount,
        reported_at=invoice.reported_at,
        paid_at=invoice.paid_at,
    )


def executors_visible(expertise: Expertise, viewer: User) -> bool:
    """Видны ли ФИО исполнителей. Заказчик аудита узнаёт состав группы только из Плана."""

    if viewer.role == UserRole.EXPERT or expertise.service != ServiceKind.AUDIT:
        return True

    return expertise.plan_sent_at is not None


class ExpertisePresenter:
    """Собирает ExpertiseOutSchema: имена сторон, платежи, группа и План аудита."""

    def __init__(
        self,
        viewer: User,
        users: UserRepository,
        payments: PaymentRepository,
        profiles: ExpertProfileRepository,
    ) -> None:
        self.viewer = viewer
        self.users = users
        self.payments = payments
        self.profiles = profiles

    async def team(self, expertise: Expertise) -> list[AuditTeamMemberSchema]:
        """Аудиторская группа с областями аттестации."""

        if expertise.service != ServiceKind.AUDIT:
            return []

        members = await load_team(expertise, self.users, self.profiles)

        return [
            AuditTeamMemberSchema(
                user_id=member.user_id,
                full_name=member.full_name,
                areas=member.areas,
                lead=member.lead,
            )
            for member in members
        ]

    async def build(self, expertise: Expertise) -> ExpertiseOutSchema:
        """Схема заявки для текущего пользователя."""

        customer = await self.users.get_by_id(expertise.customer_id)
        visible = executors_visible(expertise, self.viewer)

        expert = None
        if visible and expertise.expert_id is not None:
            expert = await self.users.get_by_id(expertise.expert_id)

        advance = None
        if expertise.advance_payment_id is not None:
            advance = await self.payments.get_by_id(expertise.advance_payment_id)

        final = None
        if expertise.final_payment_id is not None:
            final = await self.payments.get_by_id(expertise.final_payment_id)

        unpaid = pending_invoice(expertise)
        team = await self.team(expertise) if visible else []

        return ExpertiseOutSchema(
            id=expertise.id,
            service=expertise.service,
            customer_id=expertise.customer_id,
            customer_name=customer.full_name if customer else "—",
            expert_id=expertise.expert_id,
            expert_name=expert.full_name if expert else None,
            object_code=expertise.object_code,
            area_code=expertise.area_code,
            hazard_class=expertise.hazard_class,
            expert_category=expertise.expert_category,
            deadline=expertise.deadline,
            object_name=expertise.object_name,
            contract_kind=expertise.contract_kind,
            customer_type=expertise.customer_type,
            company=ExpertiseCompanySchema.model_validate(expertise.company)
            if expertise.company
            else None,
            individual=ExpertiseIndividualSchema.model_validate(expertise.individual)
            if expertise.individual
            else None,
            audit_details=AuditDetailsSchema.model_validate(expertise.audit_details)
            if expertise.audit_details
            else None,
            comment=expertise.comment,
            status=expertise.status,
            result=expertise.result,
            price=expertise.price,
            offer_price=expertise.offer_price,
            counter_price=expertise.counter_price,
            audit_plan=AuditPlanSchema.model_validate(expertise.audit_plan)
            if expertise.audit_plan
            else None,
            plan_comment=expertise.plan_comment,
            team=team,
            advance_payment=ExpertisePaymentSchema.model_validate(advance) if advance else None,
            final_payment=ExpertisePaymentSchema.model_validate(final) if final else None,
            invoice=to_invoice_schema(unpaid) if unpaid else None,
            created_at=expertise.created_at,
            expert_ready_at=expertise.expert_ready_at,
            contract_at=expertise.contract_at,
            advance_paid_at=expertise.advance_paid_at,
            plan_sent_at=expertise.plan_sent_at,
            plan_approved_at=expertise.plan_approved_at,
            conclusion_ready_at=expertise.conclusion_ready_at,
            final_paid_at=expertise.final_paid_at,
            sent_at=expertise.sent_at,
            accepted_at=expertise.accepted_at,
            documents=expertise.documents,
            remarks=expertise.remarks,
        )
