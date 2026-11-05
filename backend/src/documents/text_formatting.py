"""Имена и даты в документах."""

from datetime import date, datetime

from src.documents.options import MOSCOW_TIMEZONE


def format_initials(*, full_name: str) -> str:
    """Сократить имя и отчество до инициалов."""

    parts = full_name.split()

    if not parts:
        return ""

    surname, *names = parts
    initials = "".join(f"{name[0]}." for name in names)

    return f"{initials} {surname}" if initials else surname


def format_period(
    *,
    start: date | None,
    end: date | None,
) -> str:
    """Записать период дат."""

    if start is None or end is None:
        return "—"

    return f"{start:%d.%m.%Y} — {end:%d.%m.%Y}"


def format_moscow_time(*, moment: datetime) -> str:
    """Записать дату и время по Москве."""

    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=MOSCOW_TIMEZONE)

    return f"{moment.astimezone(MOSCOW_TIMEZONE):%d.%m.%Y %H:%M} (МСК)"
