"""Название объектов заявки."""

from src.audit.options import OBJECT_NAME_MAX_LENGTH
from src.audit.schemas.audit_details import AuditDetailsSchema


def describe_audit_objects(*, details: AuditDetailsSchema) -> str:
    """Составить название для списка заявок."""

    if details.scope == "all" and details.fleet is not None:
        object_name = f"Все ОПО {details.applicant.organization} ({details.fleet.count})"
    else:
        object_name = "; ".join(
            f"{audit_object.name} ({audit_object.reg_number})" for audit_object in details.objects
        )

    return object_name[:OBJECT_NAME_MAX_LENGTH]
