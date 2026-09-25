"""Письма участникам экспертизы на каждом шаге. В кабинете дублируются уведомлениями."""

from app.models.expertise import Expertise
from app.models.user import User
from app.services.experts.catalog import AREA_BY_CODE, OBJECT_BY_CODE
from app.services.mail.sender import send_email

SITE_URL = "https://nedra-npi.ru"
CABINET_LINE = f"Заявка в личном кабинете: {SITE_URL}/kabinet"


def describe_expertise(expertise: Expertise) -> str:
    """Короткое описание заявки для писем и уведомлений: объект, область, категория."""

    object_label = OBJECT_BY_CODE[expertise.object_code].label
    area = AREA_BY_CODE[expertise.area_code]

    return f"{object_label}, {area.code} ({area.title}), категория {expertise.expert_category}"


def format_price(expertise: Expertise) -> str:
    """Стоимость в рублях без копеек для письма."""

    if expertise.price is None:
        return "по запросу"

    return f"{int(expertise.price):,} ₽".replace(",", " ")


async def send_new_expertise_letters(expertise: Expertise, experts: list[User]) -> None:
    """Каждому подходящему эксперту — письмо о новой заявке."""

    description = describe_expertise(expertise)

    for expert in experts:
        await send_email(
            recipients=[expert.email],
            subject=f"Новая заявка на экспертизу №{expertise.id} — НПИ «Недра»",
            text=(
                f"{expert.full_name}, поступила заявка по вашей области аттестации.\n\n"
                f"{description}.\n\n{CABINET_LINE}"
            ),
        )


async def send_expert_ready_letter(expertise: Expertise, customer: User, expert: User) -> None:
    """Заказчику: эксперт готов, ознакомьтесь с договором и подпишите его."""

    await send_email(
        recipients=[customer.email],
        subject=f"Эксперт готов провести экспертизу №{expertise.id} — НПИ «Недра»",
        text=(
            f"{customer.full_name}, эксперт {expert.full_name} готов провести экспертизу "
            f"по вашей заявке.\n\n{describe_expertise(expertise)}.\n"
            f"Стоимость: {format_price(expertise)}, оплата двумя частями по 50 %.\n\n"
            "Ознакомьтесь с договором в кабинете и согласитесь с его условиями, "
            f"после этого договор будет заключён.\n{CABINET_LINE}"
        ),
    )


async def send_contract_letter(expertise: Expertise, expert: User) -> None:
    """Эксперту: заказчик подписал договор, ждём аванс."""

    await send_email(
        recipients=[expert.email],
        subject=f"Договор по экспертизе №{expertise.id} заключён — НПИ «Недра»",
        text=(
            f"{expert.full_name}, заказчик согласился с условиями договора по заявке "
            f"№{expertise.id}. Договор заключён. Как только поступит аванс, мы сообщим, "
            f"и можно будет приступать к работе.\n\n{CABINET_LINE}"
        ),
    )


async def send_advance_paid_letter(expertise: Expertise, expert: User) -> None:
    """Эксперту: аванс оплачен, можно работать."""

    await send_email(
        recipients=[expert.email],
        subject=f"Аванс по экспертизе №{expertise.id} оплачен — НПИ «Недра»",
        text=(
            f"{expert.full_name}, заказчик оплатил аванс по заявке №{expertise.id}. "
            "Можно приступать к экспертизе. Когда заключение будет готово, отметьте это "
            f"в кабинете.\n\n{CABINET_LINE}"
        ),
    )


async def send_remarks_letter(expertise: Expertise, customer: User, text: str | None) -> None:
    """Заказчику: по документации есть замечания, нужно исправить и прислать повторно."""

    body = f"Замечания:\n{text}\n\n" if text else ""

    await send_email(
        recipients=[customer.email],
        subject=f"Замечания по экспертизе №{expertise.id} — НПИ «Недра»",
        text=(
            f"{customer.full_name}, эксперт подготовил рекомендации по приведению объекта "
            f"экспертизы в соответствие с требованиями промышленной безопасности.\n\n{body}"
            f"Внесите изменения в документацию и отправьте её повторно.\n{CABINET_LINE}"
        ),
    )


async def send_revision_letter(expertise: Expertise, expert: User, text: str | None) -> None:
    """Эксперту: заказчик прислал исправленную документацию."""

    body = f"Комментарий заказчика:\n{text}\n\n" if text else ""

    await send_email(
        recipients=[expert.email],
        subject=f"Исправленная документация по экспертизе №{expertise.id} — НПИ «Недра»",
        text=(
            f"{expert.full_name}, заказчик исправил замечания по заявке №{expertise.id} "
            f"и прислал документацию повторно.\n\n{body}{CABINET_LINE}"
        ),
    )


async def send_conclusion_ready_letter(expertise: Expertise, customer: User) -> None:
    """Заказчику: заключение готово, оплатите остаток."""

    await send_email(
        recipients=[customer.email],
        subject=f"Заключение по экспертизе №{expertise.id} готово — НПИ «Недра»",
        text=(
            f"{customer.full_name}, эксперт подготовил заключение по заявке №{expertise.id}. "
            "Замечаний нет, документация соответствует требованиям промышленной безопасности.\n\n"
            f"Требуется полная оплата: внесите оставшиеся 50 %, и эксперт отправит "
            f"подписанное заключение.\n\n{CABINET_LINE}"
        ),
    )


async def send_final_paid_letter(expertise: Expertise, expert: User) -> None:
    """Эксперту: остаток оплачен, отправьте заключение."""

    await send_email(
        recipients=[expert.email],
        subject=f"Остаток по экспертизе №{expertise.id} оплачен — НПИ «Недра»",
        text=(
            f"{expert.full_name}, заказчик оплатил остаток по заявке №{expertise.id}. "
            f"Подпишите заключение ЭЦП и отправьте его заказчику из кабинета.\n\n{CABINET_LINE}"
        ),
    )


async def send_conclusion_sent_letter(expertise: Expertise, customer: User) -> None:
    """Заказчику: заключение отправлено, скачайте и примите работу."""

    await send_email(
        recipients=[customer.email],
        subject=f"Заключение по экспертизе №{expertise.id} отправлено — НПИ «Недра»",
        text=(
            f"{customer.full_name}, эксперт отправил заключение по заявке №{expertise.id}. "
            f"Скачайте его в кабинете и, если всё в порядке, нажмите «Работа принята».\n\n{CABINET_LINE}"
        ),
    )


async def send_work_accepted_letter(expertise: Expertise, expert: User) -> None:
    """Эксперту: заказчик принял работу."""

    await send_email(
        recipients=[expert.email],
        subject=f"Работа по экспертизе №{expertise.id} принята — НПИ «Недра»",
        text=(
            f"{expert.full_name}, заказчик принял работу по заявке №{expertise.id}. "
            f"Спасибо!\n\n{CABINET_LINE}"
        ),
    )
