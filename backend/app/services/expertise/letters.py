"""Письма экспертам о новых заявках."""

from app.models.expertise import Expertise
from app.models.user import User
from app.services.experts.catalog import AREA_BY_CODE, OBJECT_BY_CODE
from app.services.mail.sender import send_email

SITE_URL = "https://nedra-npi.ru"


def describe_expertise(expertise: Expertise) -> str:
    """Короткое описание заявки для писем и уведомлений: объект, область, категория."""

    object_label = OBJECT_BY_CODE[expertise.object_code].label
    area = AREA_BY_CODE[expertise.area_code]

    return f"{object_label}, {area.code} ({area.title}), категория {expertise.expert_category}"


async def send_new_expertise_letters(expertise: Expertise, experts: list[User]) -> None:
    """Каждому подходящему эксперту — письмо о новой заявке."""

    description = describe_expertise(expertise)

    for expert in experts:
        await send_email(
            recipients=[expert.email],
            subject=f"Новая заявка на экспертизу №{expertise.id} — НПИ «Недра»",
            text=(
                f"{expert.full_name}, поступила заявка по вашей области аттестации.\n\n"
                f"{description}.\n\n"
                f"Посмотреть заявку можно в личном кабинете: {SITE_URL}/kabinet"
            ),
        )
