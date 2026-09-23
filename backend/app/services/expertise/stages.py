"""Этапы оплаты экспертизы: аванс и остаток.

Оплатить можно картой через ЮKassa или по счёту для юрлица. Дальше экспертиза
движется одинаково, поэтому сдвиг статуса живёт здесь, а не в каждом сценарии.
"""

from datetime import datetime, timezone

from app.models.billing import InvoiceStage
from app.models.expertise import Expertise, ExpertiseStatus

STAGE_TITLES = {
    InvoiceStage.ADVANCE: "Аванс 50%",
    InvoiceStage.FINAL: "Оставшиеся 50%",
}

STAGE_BY_STATUS = {
    ExpertiseStatus.CONTRACT: InvoiceStage.ADVANCE,
    ExpertiseStatus.CONCLUSION_READY: InvoiceStage.FINAL,
}

SIGN_CONCLUSION = "sign_conclusion"


def current_stage(expertise: Expertise) -> InvoiceStage | None:
    """Этап, который заказчик оплачивает прямо сейчас, или None."""

    return STAGE_BY_STATUS.get(ExpertiseStatus(expertise.status))


def stage_notification_kind(expertise: Expertise) -> str | None:
    """Тип уведомления эксперту после оплаты этапа.

    Оплаченный остаток означает, что пора подписать заключение ЭЦП и отправить
    его заказчику — такое уведомление кабинет показывает всплывающим окном.
    """

    if expertise.status == ExpertiseStatus.PAID:
        return SIGN_CONCLUSION

    return None


def mark_stage_paid(expertise: Expertise, stage: InvoiceStage) -> str | None:
    """Сдвинуть экспертизу после оплаты этапа.

    Возвращает текст уведомления эксперту или None, если этап уже пройден:
    повторное подтверждение ничего не ломает.
    """

    now = datetime.now(timezone.utc)

    if stage == InvoiceStage.ADVANCE and expertise.status == ExpertiseStatus.CONTRACT:
        expertise.advance_paid_at = now
        expertise.status = ExpertiseStatus.IN_PROGRESS

        return f"Заказчик оплатил аванс по заявке №{expertise.id}, можно приступать к работе"

    if stage == InvoiceStage.FINAL and expertise.status == ExpertiseStatus.CONCLUSION_READY:
        expertise.final_paid_at = now
        expertise.status = ExpertiseStatus.PAID

        return f"Заказчик оплатил остаток по заявке №{expertise.id}, отправьте заключение"

    return None
