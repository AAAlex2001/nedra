"""Приглашение на вступительное совещание."""

from datetime import UTC, datetime

from src.audit.options import AUDIT_MEETING_DURATION
from src.audit.site.schemas.audit_plan import AuditPlanResponse
from src.documents.options import MOSCOW_TIMEZONE


def escape_calendar_text(*, text: str) -> str:
    """Экранировать текст календаря."""

    return (
        text.replace("\\", "\\\\")
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .replace("\n", "\\n")
        .replace(";", "\\;")
        .replace(",", "\\,")
    )


def calendar_timestamp(*, moment: datetime) -> str:
    """Записать время календаря в UTC."""

    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=MOSCOW_TIMEZONE)

    return f"{moment.astimezone(UTC):%Y%m%dT%H%M%SZ}"


def create_meeting_invitation(
    *,
    audit_id: int,
    object_name: str | None,
    plan: AuditPlanResponse,
    generated_at: datetime,
) -> bytes | None:
    """Создать приглашение для календаря."""

    if not plan.meetings or plan.opening_at is None:
        return None

    summary = escape_calendar_text(
        text=f"Вступительное совещание по аудиту СУПБ, заявка №{audit_id}"
    )
    description = escape_calendar_text(text=f"Объект аудита: {object_name or '—'}")
    location = escape_calendar_text(
        text=plan.meeting_link or "Видеосвязь, ссылку пришлёт руководитель группы",
    )
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//NPI Nedra//Blitz Audit//RU",
        "METHOD:PUBLISH",
        "BEGIN:VEVENT",
        f"UID:audit-{audit_id}-opening-{plan.version}@nedra-npi.ru",
        f"DTSTAMP:{calendar_timestamp(moment=generated_at)}",
        f"DTSTART:{calendar_timestamp(moment=plan.opening_at)}",
        f"DTEND:{calendar_timestamp(moment=plan.opening_at + AUDIT_MEETING_DURATION)}",
        f"SUMMARY:{summary}",
        f"DESCRIPTION:{description}",
        f"LOCATION:{location}",
        "END:VEVENT",
        "END:VCALENDAR",
    ]

    return ("\r\n".join(lines) + "\r\n").encode("utf-8")
