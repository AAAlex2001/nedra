"""Аудиторская группа заявки: руководитель и аудиторы с их областями аттестации."""

from dataclasses import dataclass

from app.models.expertise import Expertise
from app.services.experts.repo import ExpertProfileRepository
from app.services.users.repo import UserRepository


@dataclass(frozen=True)
class TeamMember:
    """Аудитор в группе: для Плана аудита и карточки заявки."""

    user_id: int
    full_name: str
    areas: list[str]
    lead: bool


async def describe_member(
    user_id: int, lead: bool, users: UserRepository, profiles: ExpertProfileRepository
) -> TeamMember | None:
    """ФИО и области аттестации аудитора из его удостоверений."""

    user = await users.get_by_id(user_id)
    if user is None:
        return None

    certificates = await profiles.list_certificates(user_id)
    areas = sorted({certificate.area_code for certificate in certificates})

    return TeamMember(user_id=user.id, full_name=user.full_name, areas=areas, lead=lead)


async def load_team(
    audit: Expertise, users: UserRepository, profiles: ExpertProfileRepository
) -> list[TeamMember]:
    """Руководитель группы первым, за ним остальные аудиторы."""

    ids = [(audit.expert_id, True)] if audit.expert_id is not None else []
    ids += [(member.user_id, False) for member in audit.team]

    team: list[TeamMember] = []
    for user_id, lead in ids:
        member = await describe_member(user_id, lead, users, profiles)
        if member is not None:
            team.append(member)

    return team
