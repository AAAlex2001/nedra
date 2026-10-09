"""Письма участникам экспертизы и аудита на каждом шаге. В кабинете дублируются уведомлениями."""

from app.models.expertise import Expertise, ServiceKind
from app.models.user import User
from app.services.experts.catalog import AREA_BY_CODE, OBJECT_BY_CODE
from app.services.expertise.money import format_rub
from app.services.expertise.wording import executor_title, wording_for
from app.services.mail.sender import send_email

SITE_URL = "https://nedra-npi.ru"
CABINET_LINE = f"Заявка в личном кабинете: {SITE_URL}/kabinet"


def describe_expertise(expertise: Expertise) -> str:
    """Короткое описание заявки для писем: объект, область и категория или предмет аудита."""

    if expertise.service == ServiceKind.AUDIT:
        return f"Аудит СУПБ: {expertise.object_name}"

    parts = []

    if expertise.object_code in OBJECT_BY_CODE:
        parts.append(OBJECT_BY_CODE[expertise.object_code].label)

    if expertise.area_code in AREA_BY_CODE:
        area = AREA_BY_CODE[expertise.area_code]
        parts.append(f"{area.code} ({area.title})")

    if expertise.expert_category is not None:
        parts.append(f"категория {expertise.expert_category}")

    if not parts:
        return f"Документация «{expertise.object_name}»"

    return ", ".join(parts)


def format_price(expertise: Expertise) -> str:
    """Стоимость в рублях без копеек для письма."""

    return format_rub(expertise.price)


async def send_new_expertise_letters(expertise: Expertise, experts: list[User]) -> None:
    """Каждому подходящему исполнителю — письмо о новой заявке."""

    words = wording_for(expertise)
    description = describe_expertise(expertise)
    reason = (
        "по направлению «Аудит СУПБ»"
        if expertise.service == ServiceKind.AUDIT
        else "по вашей области аттестации"
    )

    for expert in experts:
        await send_email(
            recipients=[expert.email],
            subject=f"Новая заявка на {words.work_accusative} №{expertise.id} — НПИ «Недра»",
            text=(
                f"{expert.full_name}, поступила заявка {reason}.\n\n"
                f"{description}.\nЦена заказчика: {format_price(expertise)}.\n\n{CABINET_LINE}"
            ),
        )


async def send_expert_ready_letter(expertise: Expertise, customer: User, expert: User) -> None:
    """Заказчику: исполнитель готов, ознакомьтесь с договором и подпишите его."""

    words = wording_for(expertise)
    title = executor_title(expertise, expert)

    await send_email(
        recipients=[customer.email],
        subject=f"{words.executor} готов провести {words.work_accusative} №{expertise.id} — НПИ «Недра»",
        text=(
            f"{customer.full_name}, {title[:1].lower()}{title[1:]} готов провести "
            f"{words.work_accusative} по вашей заявке.\n\n{describe_expertise(expertise)}.\n"
            f"Стоимость: {format_price(expertise)}, оплата двумя частями по 50 %.\n\n"
            "Ознакомьтесь с договором в кабинете и согласитесь с его условиями, "
            f"после этого договор будет заключён.\n{CABINET_LINE}"
        ),
    )


async def send_contract_letter(expertise: Expertise, expert: User) -> None:
    """Исполнителю: заказчик подписал договор, ждём аванс."""

    words = wording_for(expertise)

    await send_email(
        recipients=[expert.email],
        subject=f"Договор по {words.work_dative} №{expertise.id} заключён — НПИ «Недра»",
        text=(
            f"{expert.full_name}, заказчик согласился с условиями договора по заявке "
            f"№{expertise.id}. Договор заключён. Как только поступит аванс, мы сообщим, "
            f"и можно будет приступать к работе.\n\n{CABINET_LINE}"
        ),
    )


async def send_advance_paid_letter(expertise: Expertise, expert: User) -> None:
    """Исполнителю: аванс оплачен, можно работать."""

    words = wording_for(expertise)

    await send_email(
        recipients=[expert.email],
        subject=f"Аванс по {words.work_dative} №{expertise.id} оплачен — НПИ «Недра»",
        text=(
            f"{expert.full_name}, заказчик оплатил аванс по заявке №{expertise.id}. "
            f"Можно приступать к работе. Когда {words.result_lower} будет {words.result_ready}, "
            f"отметьте это в кабинете.\n\n{CABINET_LINE}"
        ),
    )


async def send_remarks_letter(expertise: Expertise, customer: User, text: str | None) -> None:
    """Заказчику: есть замечания, нужно исправить и прислать повторно."""

    words = wording_for(expertise)
    body = f"Замечания:\n{text}\n\n" if text else ""

    await send_email(
        recipients=[customer.email],
        subject=f"Замечания по {words.work_dative} №{expertise.id} — НПИ «Недра»",
        text=(
            f"{customer.full_name}, {words.executor_lower} подготовил замечания по представленным "
            f"документам.\n\n{body}"
            f"Внесите изменения и отправьте документы повторно.\n{CABINET_LINE}"
        ),
    )


async def send_revision_letter(expertise: Expertise, expert: User, text: str | None) -> None:
    """Исполнителю: заказчик прислал исправленные документы."""

    words = wording_for(expertise)
    body = f"Комментарий заказчика:\n{text}\n\n" if text else ""

    await send_email(
        recipients=[expert.email],
        subject=f"Исправленные документы по {words.work_dative} №{expertise.id} — НПИ «Недра»",
        text=(
            f"{expert.full_name}, заказчик исправил замечания по заявке №{expertise.id} "
            f"и прислал документы повторно.\n\n{body}{CABINET_LINE}"
        ),
    )


async def send_conclusion_ready_letter(expertise: Expertise, customer: User) -> None:
    """Заказчику: итоговый документ готов, оплатите остаток."""

    words = wording_for(expertise)

    await send_email(
        recipients=[customer.email],
        subject=f"{words.result} по заявке №{expertise.id} {words.result_ready} — НПИ «Недра»",
        text=(
            f"{customer.full_name}, {words.executor_lower} подготовил {words.result_lower} "
            f"по заявке №{expertise.id}.\n\n"
            f"Внесите оставшиеся 50 %, и {words.executor_lower} отправит подписанный документ.\n\n"
            f"{CABINET_LINE}"
        ),
    )


async def send_final_paid_letter(expertise: Expertise, expert: User) -> None:
    """Исполнителю: остаток оплачен, отправьте итоговый документ."""

    words = wording_for(expertise)

    await send_email(
        recipients=[expert.email],
        subject=f"Остаток по {words.work_dative} №{expertise.id} оплачен — НПИ «Недра»",
        text=(
            f"{expert.full_name}, заказчик оплатил остаток по заявке №{expertise.id}. "
            f"Подпишите {words.result_lower} ЭЦП и отправьте заказчику из кабинета.\n\n{CABINET_LINE}"
        ),
    )


async def send_conclusion_sent_letter(expertise: Expertise, customer: User) -> None:
    """Заказчику: итоговый документ отправлен, скачайте и примите работу."""

    words = wording_for(expertise)

    await send_email(
        recipients=[customer.email],
        subject=f"{words.result} по заявке №{expertise.id} {words.result_sent} — НПИ «Недра»",
        text=(
            f"{customer.full_name}, {words.executor_lower} отправил {words.result_lower} "
            f"по заявке №{expertise.id}. Скачайте документ в кабинете и, если всё в порядке, "
            f"нажмите «Работа принята».\n\n{CABINET_LINE}"
        ),
    )


async def send_work_accepted_letter(expertise: Expertise, expert: User) -> None:
    """Исполнителю: заказчик принял работу."""

    words = wording_for(expertise)

    await send_email(
        recipients=[expert.email],
        subject=f"Работа по {words.work_dative} №{expertise.id} принята — НПИ «Недра»",
        text=(
            f"{expert.full_name}, заказчик принял работу по заявке №{expertise.id}. "
            f"Спасибо!\n\n{CABINET_LINE}"
        ),
    )
