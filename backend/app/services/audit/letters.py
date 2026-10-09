"""Письма по аудиту СУПБ: консультация, торг по цене и План аудита.

Заказчик до Плана видит только «Аудитор НПИ «Недра»», поэтому ФИО аудиторов
в письмах заказчику не пишем.
"""

from decimal import Decimal

from app.config import get_settings
from app.models.expertise import Expertise
from app.models.user import User
from app.schemas.audit_details import AuditDetailsSchema, AuditPlanSchema
from app.services.audit.invite import INVITE_FILENAME, INVITE_TYPE
from app.services.audit.options import AUDIT_KINDS
from app.services.audit.plan_document import moscow_time
from app.services.expertise.money import format_rub
from app.services.mail.sender import Attachment, send_email

SITE_URL = "https://nedra-npi.ru"
CABINET_LINE = f"Заявка в личном кабинете: {SITE_URL}/kabinet"


def rub(amount: Decimal | None) -> str:
    """Сумма для письма: 150 000 ₽."""

    return format_rub(amount, empty="не указана")


async def send_consultation_letter(audit: Expertise) -> None:
    """Менеджеру: заказчику нужна консультация по типу аудита, свяжитесь с ним."""

    details = AuditDetailsSchema.model_validate(audit.audit_details)
    applicant = details.applicant

    await send_email(
        recipients=get_settings().notify_emails,
        subject=f"Аудит СУПБ №{audit.id}: нужна консультация по типу аудита",
        text=(
            f"{applicant.full_name} ({applicant.position}, {applicant.organization}, "
            f"ИНН {applicant.inn}) просит консультацию для определения типа аудита.\n\n"
            f"Телефон: {applicant.phone}\nE-mail: {applicant.email}\n"
            f"Объект аудита: {audit.object_name}\n\n"
            "Свяжитесь с заказчиком, уточните параметры и откройте заявку аудиторам: "
            "в админке поставьте статус «Ждёт аудитора»."
        ),
    )


async def send_offer_letter(audit: Expertise, customer: User) -> None:
    """Заказчику: аудитор предложил цену, ответьте в кабинете."""

    await send_email(
        recipients=[customer.email],
        subject=f"Предложение по цене аудита №{audit.id} — НПИ «Недра»",
        text=(
            f"{customer.full_name}, аудитор НПИ «Недра» изучил заявку и предложил цену "
            f"{rub(audit.offer_price)}.\n\n"
            "В кабинете вы можете принять цену, предложить свою или отказаться.\n"
            f"{CABINET_LINE}"
        ),
    )


async def send_offer_answered_letter(audit: Expertise, lead: User, answer: str) -> None:
    """Руководителю группы: заказчик ответил на предложение по цене."""

    if answer == "accept":
        body = f"заказчик принял цену {rub(audit.price)}. Ждём подписания договора"
    elif answer == "counter":
        body = (
            f"заказчик предложил {rub(audit.counter_price)} вместо {rub(audit.offer_price)}. "
            "Примите цену заказчика или откажитесь от заявки"
        )
    else:
        body = "заказчик отказался от предложенной цены. Заявка вернулась в общий список"

    await send_email(
        recipients=[lead.email],
        subject=f"Ответ заказчика по цене аудита №{audit.id} — НПИ «Недра»",
        text=f"{lead.full_name}, {body}.\n\n{CABINET_LINE}",
    )


async def send_counter_answered_letter(audit: Expertise, customer: User, accepted: bool) -> None:
    """Заказчику: аудитор ответил на предложенную им цену."""

    if accepted:
        body = (
            f"аудитор НПИ «Недра» согласился на цену {rub(audit.price)}. Ознакомьтесь "
            "с договором в кабинете и подпишите его"
        )
    else:
        body = (
            "аудитор не согласился на предложенную цену. Заявка вернулась в общий список, "
            "её может взять другой аудитор"
        )

    await send_email(
        recipients=[customer.email],
        subject=f"Ответ по цене аудита №{audit.id} — НПИ «Недра»",
        text=f"{customer.full_name}, {body}.\n\n{CABINET_LINE}",
    )


async def send_plan_letter(audit: Expertise, customer: User) -> None:
    """Заказчику: План аудита ждёт согласования."""

    await send_email(
        recipients=[customer.email],
        subject=f"План аудита №{audit.id} ждёт согласования — НПИ «Недра»",
        text=(
            f"{customer.full_name}, руководитель аудиторской группы подготовил План проведения "
            "аудита: состав группы, график работ и запрашиваемые ресурсы.\n\n"
            "Откройте План в кабинете и согласуйте его или запросите корректировки.\n"
            f"{CABINET_LINE}"
        ),
    )


async def send_plan_changes_letter(audit: Expertise, lead: User) -> None:
    """Руководителю группы: заказчик просит скорректировать План."""

    await send_email(
        recipients=[lead.email],
        subject=f"Корректировки Плана аудита №{audit.id} — НПИ «Недра»",
        text=(
            f"{lead.full_name}, заказчик просит скорректировать План аудита.\n\n"
            f"Комментарий заказчика:\n{audit.plan_comment}\n\n"
            f"Внесите изменения и отправьте новую версию.\n{CABINET_LINE}"
        ),
    )


def meeting_text(plan: AuditPlanSchema) -> str:
    """Строки о вступительном совещании для письма. Пусто, если совещаний нет."""

    if not plan.meetings or plan.opening_at is None:
        return ""

    text = f"\n\nВступительное совещание: {moscow_time(plan.opening_at)}."

    if plan.meeting_link:
        text += f"\nСсылка для подключения: {plan.meeting_link}"

    return text + "\nПриглашение для календаря — во вложении."


async def send_plan_approved_letters(
    audit: Expertise, customer: User, team: list[User], invite: bytes | None
) -> None:
    """Группе и заказчику: План согласован. Если есть совещание — приглашение в календарь."""

    plan = AuditPlanSchema.model_validate(audit.audit_plan)
    details = AuditDetailsSchema.model_validate(audit.audit_details)
    meeting = meeting_text(plan)

    attachments = []
    if invite is not None:
        attachments.append(Attachment(INVITE_FILENAME, INVITE_TYPE, invite))

    for member in team:
        await send_email(
            recipients=[member.email],
            subject=f"План аудита №{audit.id} согласован — НПИ «Недра»",
            text=(
                f"{member.full_name}, заказчик согласовал План аудита "
                f"({AUDIT_KINDS[details.params.kind]}). Документы открыты для проверки."
                f"{meeting}\n\n{CABINET_LINE}"
            ),
            attachments=attachments,
        )

    await send_email(
        recipients=[customer.email],
        subject=f"План аудита №{audit.id} согласован — НПИ «Недра»",
        text=(
            f"{customer.full_name}, вы согласовали План аудита. Загрузите документы по перечню "
            f"в кабинете — аудиторская группа приступает к проверке.{meeting}\n\n{CABINET_LINE}"
        ),
        attachments=attachments,
    )
