"""Слова для писем, уведомлений, счетов и актов: экспертиза и аудит называют вещи по-разному."""

from dataclasses import dataclass

from app.models.expertise import Expertise, ServiceKind


@dataclass(frozen=True)
class Wording:
    """Формы слов, которые меняются от сервиса к сервису."""

    executor: str
    executor_lower: str
    work_nominative: str
    work_accusative: str
    work_dative: str
    result: str
    result_lower: str
    result_ready: str
    result_sent: str
    invoice_subject: str


EXPERTISE_WORDING = Wording(
    executor="Эксперт",
    executor_lower="эксперт",
    work_nominative="Экспертиза",
    work_accusative="экспертизу",
    work_dative="экспертизе",
    result="Заключение",
    result_lower="заключение",
    result_ready="готово",
    result_sent="отправлено",
    invoice_subject="экспертизу промышленной безопасности",
)

AUDIT_WORDING = Wording(
    executor="Аудитор",
    executor_lower="аудитор",
    work_nominative="Аудит СУПБ",
    work_accusative="аудит СУПБ",
    work_dative="аудиту СУПБ",
    result="Отчёт об аудите",
    result_lower="отчёт об аудите",
    result_ready="готов",
    result_sent="отправлен",
    invoice_subject="аудит системы управления промышленной безопасностью",
)


def wording_for(expertise: Expertise) -> Wording:
    """Формулировки под сервис заявки."""

    if expertise.service == ServiceKind.AUDIT:
        return AUDIT_WORDING

    return EXPERTISE_WORDING
