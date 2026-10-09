"""Приглашение на вступительное совещание файлом календаря (.ics)."""

from datetime import datetime, timedelta, timezone

from app.models.expertise import Expertise
from app.schemas.audit_details import AuditPlanSchema
from app.services.audit.plan_document import MOSCOW

MEETING_LENGTH = timedelta(hours=1)
INVITE_FILENAME = "Вступительное совещание.ics"
INVITE_TYPE = "text/calendar"


def escape(text: str) -> str:
    """Экранировать текст для поля календаря."""

    return (
        text.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")
    )


def utc_stamp(moment: datetime) -> str:
    """Время в формате календаря, в UTC: 20261115T070000Z."""

    aware = moment if moment.tzinfo else moment.replace(tzinfo=MOSCOW)

    return f"{aware.astimezone(timezone.utc):%Y%m%dT%H%M%SZ}"


def build_invite(audit: Expertise, plan: AuditPlanSchema, now: datetime) -> bytes | None:
    """Событие на время вступительного совещания. None — совещаний по Плану нет."""

    if not plan.meetings or plan.opening_at is None:
        return None

    summary = f"Вступительное совещание по аудиту СУПБ, заявка №{audit.id}"
    description = f"Объект аудита: {audit.object_name or '—'}"
    location = plan.meeting_link or "Видеосвязь, ссылку пришлёт руководитель группы"

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//NPI Nedra//Blitz Audit//RU",
        "METHOD:PUBLISH",
        "BEGIN:VEVENT",
        f"UID:audit-{audit.id}-opening-{plan.version}@nedra-npi.ru",
        f"DTSTAMP:{utc_stamp(now)}",
        f"DTSTART:{utc_stamp(plan.opening_at)}",
        f"DTEND:{utc_stamp(plan.opening_at + MEETING_LENGTH)}",
        f"SUMMARY:{escape(summary)}",
        f"DESCRIPTION:{escape(description)}",
        f"LOCATION:{escape(location)}",
        "END:VEVENT",
        "END:VCALENDAR",
    ]

    return ("\r\n".join(lines) + "\r\n").encode()
