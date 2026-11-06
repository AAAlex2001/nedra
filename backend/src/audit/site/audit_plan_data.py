"""Данные для программы аудита."""

from dataclasses import dataclass

from src.audit.models.audit_company import AuditCompany
from src.audit.schemas.audit_details import AuditDetailsSchema
from src.audit.site.schemas.audit_team import AuditTeamMemberResponse


@dataclass(kw_only=True)
class AuditPlanData:
    """Анкета, реквизиты и группа для документа."""

    audit_id: int  # Номер аудита.
    details: AuditDetailsSchema  # Объём проверки из анкеты.
    company: AuditCompany | None  # Реквизиты заказчика.
    team: list[AuditTeamMemberResponse]  # Состав аудиторской группы.
