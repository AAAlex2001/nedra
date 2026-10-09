"""Программа аудита СУПБ в Word по шаблону института.

Шаблон — документ заказчика, где вместо пустых ячеек стоят метки {{...}}.
Заполняются они той же функцией, что и договор.
"""

from datetime import date, datetime, timedelta, timezone
from io import BytesIO
from pathlib import Path

from docx import Document

from app.models.expertise import Expertise
from app.schemas.audit_details import AuditDetailsSchema, AuditPlanSchema
from app.services.audit.options import AUDIT_KINDS, ELEMENTS
from app.services.audit.team import TeamMember
from app.services.contracts.document import fill, initials

TEMPLATE = Path(__file__).parent / "templates" / "audit_program.docx"

MOSCOW = timezone(timedelta(hours=3))

SCOPE_TEXT = {
    "basic": "Объем аудита определяется как всесторонняя проверка всех элементов СУПБ.",
    "interim": "Оценка выполнения корректирующих мероприятий по результатам базового аудита СУПБ.",
    "consultation": "Объем аудита согласован с заказчиком по итогам консультации.",
}


def moscow_time(moment: datetime) -> str:
    """Дата и время по Москве: 15.11.2026 10:00 (МСК)."""

    aware = moment if moment.tzinfo else moment.replace(tzinfo=MOSCOW)

    return f"{aware.astimezone(MOSCOW):%d.%m.%Y %H:%M} (МСК)"


def period(start: date | None, end: date | None) -> str:
    """Период дат: 01.11.2026 — 10.11.2026."""

    if start is None or end is None:
        return "—"

    return f"{start:%d.%m.%Y} — {end:%d.%m.%Y}"


def audit_scope(details: AuditDetailsSchema) -> str:
    """Объем аудита: для выборочного — перечень элементов СУПБ."""

    if details.params.kind != "selective":
        return SCOPE_TEXT[details.params.kind]

    elements = [ELEMENTS[element] for element in details.params.elements]

    return "Выборочная проверка элементов СУПБ:\n" + "\n".join(elements)


def objects_text(details: AuditDetailsSchema) -> str:
    """Проверяемые ОПО: по одному на строку или сведения обо всех ОПО."""

    if details.fleet is not None:
        return f"Все ОПО организации, количество: {details.fleet.count}"

    lines = [f"{item.name}, {item.hazard_class} класс опасности" for item in details.objects]

    return "\n".join(lines)


def reg_numbers_text(details: AuditDetailsSchema) -> str:
    """Регистрационные номера ОПО."""

    if details.fleet is not None:
        return "Согласно свидетельству о регистрации ОПО"

    return "\n".join(item.reg_number for item in details.objects)


def address_text(audit: Expertise, details: AuditDetailsSchema) -> str:
    """Адрес проведения аудита: адреса ОПО или юридический адрес организации."""

    if details.fleet is None:
        return "\n".join(item.address for item in details.objects)

    if audit.company is None:
        return "—"

    return audit.company.address


def overall_period(plan: AuditPlanSchema) -> str:
    """Сроки проведения: от начала документарного этапа до конца последнего этапа."""

    end = plan.documents_end
    if plan.onsite_end is not None and plan.onsite_end > end:
        end = plan.onsite_end

    return period(plan.documents_start, end)


def member_line(member: TeamMember) -> str:
    """Аудитор и его области аттестации."""

    areas = ", ".join(member.areas) or "—"

    return f"{member.full_name}, области аттестации: {areas}"


def team_values(team: list[TeamMember]) -> dict[str, str]:
    """Руководитель и состав аудиторской группы."""

    lead = next((member for member in team if member.lead), None)
    others = [member_line(member) for member in team if not member.lead]

    return {
        "lead": member_line(lead) if lead else "—",
        "lead_name": lead.full_name if lead else "",
        "lead_initials": initials(lead.full_name) if lead else "",
        "team": "\n".join(others) or "—",
    }


def schedule_values(plan: AuditPlanSchema, generated_at: datetime) -> dict[str, str]:
    """Даты мероприятий в графике проведения аудита."""

    documents = period(plan.documents_start, plan.documents_end)
    onsite = period(plan.onsite_start, plan.onsite_end) if plan.onsite_start else "Не предусмотрен"
    no_meetings = "Не проводится"

    return {
        "date_opening": moscow_time(plan.opening_at) if plan.opening_at else no_meetings,
        "date_preparation": f"{generated_at:%d.%m.%Y}",
        "date_documents": documents,
        "date_onsite": onsite,
        "date_interview": onsite if plan.onsite_start else documents,
        "date_closing": moscow_time(plan.closing_at) if plan.closing_at else no_meetings,
        "date_report": "По завершении проверки",
        "date_delivery": "После оплаты остатка",
        "workshops": plan.workshops or "",
        "interviewees": plan.interviewees,
    }


def customer_values(audit: Expertise, details: AuditDetailsSchema) -> dict[str, str]:
    """Заказчик в шапке, в критериях аудита и в сведениях об объекте."""

    company = audit.company
    sto = f", в том числе {details.params.sto_name}" if details.params.use_sto else ""

    return {
        "customer_name": company.name if company else details.applicant.organization,
        "customer_signer": initials(company.signer_name) if company else "",
        "organization": company.full_name if company else details.applicant.organization,
        "sto": sto,
    }


def build_plan_document(
    audit: Expertise,
    details: AuditDetailsSchema,
    plan: AuditPlanSchema,
    team: list[TeamMember],
    generated_at: datetime,
) -> bytes:
    """Собрать Программу аудита по шаблону института."""

    values = {
        **customer_values(audit, details),
        **team_values(team),
        **schedule_values(plan, generated_at),
        "address": address_text(audit, details),
        "objects": objects_text(details),
        "reg_numbers": reg_numbers_text(details),
        "audit_kind": AUDIT_KINDS[details.params.kind],
        "audit_scope": audit_scope(details),
        "period": overall_period(plan),
    }

    document = Document(str(TEMPLATE))
    fill(document, values)

    buffer = BytesIO()
    document.save(buffer)

    return buffer.getvalue()


def plan_filename(audit: Expertise, version: int) -> str:
    """Имя файла Программы для скачивания."""

    return f"Программа аудита — заявка {audit.id}, версия {version}.docx"
