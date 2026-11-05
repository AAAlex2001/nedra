"""Проверка анкеты и приглашения на аудит."""

from datetime import UTC, date, datetime

import pytest
from pydantic import ValidationError

from src.audit.schemas.audit_details import (
    AuditDetailsSchema,
    AuditParametersSchema,
    AuditTimingSchema,
)
from src.audit.site.documents.meeting_invitation import create_meeting_invitation
from src.audit.site.schemas.audit_plan import AuditPlanResponse
from src.audit.site.schemas.create_audit import CreateAuditRequest


@pytest.mark.parametrize("scope", ["one", "selected", "all"])
def test_objects_are_required(audit_payload: CreateAuditRequest, scope: str) -> None:
    details = audit_payload.details.model_dump()
    details.update(scope=scope, objects=[], fleet=None)

    with pytest.raises(ValidationError):
        AuditDetailsSchema.model_validate(details)


@pytest.mark.parametrize(
    "parameters",
    [
        {"kind": "basic"},
        {"kind": "interim", "use_sto": True, "sto_name": " "},
        {"kind": "selective", "elements": []},
    ],
)
def test_audit_parameters_require_selected_details(parameters: dict) -> None:
    with pytest.raises(ValidationError):
        AuditParametersSchema.model_validate(parameters)


@pytest.mark.parametrize("end", [None, date(2026, 12, 1)])
def test_custom_period_requires_ordered_dates(end: date | None) -> None:
    with pytest.raises(ValidationError):
        AuditTimingSchema(kind="custom", start=date(2026, 12, 10), end=end)


@pytest.mark.parametrize(
    ("budget_mode", "price"),
    [("custom", "99999"), ("custom", None), ("none", "500000")],
)
def test_budget_matches_price(
    audit_payload: CreateAuditRequest, budget_mode: str, price: str | None
) -> None:
    payload = audit_payload.model_dump()
    payload["details"]["budget"]["mode"] = budget_mode
    payload["price"] = price

    with pytest.raises(ValidationError):
        CreateAuditRequest.model_validate(payload)


def test_individual_cannot_order_audit(audit_payload: CreateAuditRequest) -> None:
    payload = audit_payload.model_dump()
    payload["customer_type"] = "individual"

    with pytest.raises(ValidationError):
        CreateAuditRequest.model_validate(payload)


def test_opening_meeting_invitation_uses_moscow_time() -> None:
    plan = AuditPlanResponse(
        documents_start=date(2026, 11, 2),
        documents_end=date(2026, 11, 5),
        opening_at=datetime(2026, 11, 2, 10),
        closing_at=datetime(2026, 11, 5, 10),
        interviewees="Главный инженер",
    )
    invitation = create_meeting_invitation(
        audit_id=1,
        object_name="Котельная",
        plan=plan,
        generated_at=datetime(2026, 10, 20, tzinfo=UTC),
    )

    assert invitation is not None
    assert b"BEGIN:VEVENT" in invitation
    assert b"DTSTART:20261102T070000Z" in invitation
    assert b"DTEND:20261102T080000Z" in invitation

    plan.meetings = False
    assert (
        create_meeting_invitation(
            audit_id=1,
            object_name="Котельная",
            plan=plan,
            generated_at=datetime(2026, 10, 20, tzinfo=UTC),
        )
        is None
    )
