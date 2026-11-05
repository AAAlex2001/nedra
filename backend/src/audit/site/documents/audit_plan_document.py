"""Программа аудита по шаблону института."""

from datetime import datetime
from io import BytesIO

from docx import Document

from src.audit.options import (
    AUDIT_ELEMENT_TITLES,
    AUDIT_KIND_TITLES,
    AUDIT_PLAN_TEMPLATE,
    AUDIT_SCOPE_TEXT,
)
from src.audit.schemas.audit_details import AuditDetailsSchema
from src.audit.site.audit_plan_data import AuditPlanData
from src.audit.site.schemas.audit_plan import AuditPlanResponse, AuditTeamMemberResponse
from src.documents.text_formatting import format_initials, format_moscow_time, format_period
from src.documents.word_template import fill_word_template


def describe_audit_scope(*, details: AuditDetailsSchema) -> str:
    """Описать объём проверки."""

    if details.params.kind != "selective":
        return AUDIT_SCOPE_TEXT[details.params.kind]

    elements = [AUDIT_ELEMENT_TITLES[element] for element in details.params.elements]

    return "Выборочная проверка элементов СУПБ:\n" + "\n".join(elements)


def describe_team_member(*, member: AuditTeamMemberResponse) -> str:
    """Указать ФИО и области аттестации."""

    areas = ", ".join(member.areas) or "—"

    return f"{member.full_name}, области аттестации: {areas}"


def team_template_values(*, team: list[AuditTeamMemberResponse]) -> dict[str, str]:
    """Подготовить состав группы для шаблона."""

    lead = None
    auditors = []

    for member in team:
        if member.lead:
            lead = member
        else:
            auditors.append(describe_team_member(member=member))

    return {
        "lead": describe_team_member(member=lead) if lead is not None else "—",
        "lead_name": lead.full_name if lead is not None else "",
        "lead_initials": format_initials(full_name=lead.full_name) if lead is not None else "",
        "team": "\n".join(auditors) or "—",
    }


def schedule_template_values(
    *,
    plan: AuditPlanResponse,
    generated_at: datetime,
) -> dict[str, str]:
    """Подготовить график для шаблона."""

    documents_period = format_period(
        start=plan.documents_start,
        end=plan.documents_end,
    )
    onsite_period = "Не предусмотрен"
    opening_time = "Не проводится"
    closing_time = "Не проводится"
    end_date = plan.documents_end

    if plan.onsite_start is not None:
        onsite_period = format_period(
            start=plan.onsite_start,
            end=plan.onsite_end,
        )

    if plan.onsite_end is not None:
        end_date = max(end_date, plan.onsite_end)

    if plan.meetings and plan.opening_at is not None:
        opening_time = format_moscow_time(moment=plan.opening_at)

    if plan.meetings and plan.closing_at is not None:
        closing_time = format_moscow_time(moment=plan.closing_at)

    return {
        "date_opening": opening_time,
        "date_preparation": f"{generated_at:%d.%m.%Y}",
        "date_documents": documents_period,
        "date_onsite": onsite_period,
        "date_interview": onsite_period if plan.onsite_start is not None else documents_period,
        "date_closing": closing_time,
        "date_report": "По завершении проверки",
        "date_delivery": "После оплаты остатка",
        "workshops": plan.workshops or "",
        "interviewees": plan.interviewees,
        "period": format_period(
            start=plan.documents_start,
            end=end_date,
        ),
    }


def create_audit_plan_document(
    *,
    plan_details: AuditPlanData,
    plan: AuditPlanResponse,
    generated_at: datetime,
) -> bytes:
    """Создать программу аудита в Word."""

    details = plan_details.details

    if details is None:
        raise ValueError("В заявке нет анкеты аудита")

    company = plan_details.company
    values = {
        "customer_name": company.name if company is not None else details.applicant.organization,
        "customer_signer": format_initials(full_name=company.signer_name)
        if company is not None
        else "",
        "organization": company.full_name
        if company is not None
        else details.applicant.organization,
        "sto": f", в том числе {details.params.sto_name}" if details.params.use_sto else "",
        "audit_kind": AUDIT_KIND_TITLES[details.params.kind],
        "audit_scope": describe_audit_scope(details=details),
    }

    if details.scope == "all" and details.fleet is not None:
        values["objects"] = f"Все ОПО организации, количество: {details.fleet.count}"
        values["reg_numbers"] = "Согласно свидетельству о регистрации ОПО"
        values["address"] = company.address if company is not None else "—"
    else:
        values["objects"] = "\n".join(
            f"{audit_object.name}, {audit_object.hazard_class} класс опасности"
            for audit_object in details.objects
        )
        values["reg_numbers"] = "\n".join(
            audit_object.reg_number for audit_object in details.objects
        )
        values["address"] = "\n".join(audit_object.address for audit_object in details.objects)

    values.update(team_template_values(team=plan_details.team))
    values.update(
        schedule_template_values(
            plan=plan,
            generated_at=generated_at,
        )
    )

    document = Document(str(AUDIT_PLAN_TEMPLATE))
    fill_word_template(
        document=document,
        values=values,
    )
    output = BytesIO()
    document.save(output)

    return output.getvalue()
