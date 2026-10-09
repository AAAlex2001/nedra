"""Кто может видеть заявку и её файлы."""

from app.models.expert import ExpertCertificate
from app.models.expertise import Expertise
from app.models.user import User, UserRole
from app.services.expertise.repo import executor_fits


def in_team(expertise: Expertise, user: User) -> bool:
    """Входит ли эксперт в аудиторскую группу заявки."""

    return any(member.user_id == user.id for member in expertise.team)


def can_view(
    expertise: Expertise, user: User, certificates: list[ExpertCertificate], audit_lead: bool
) -> bool:
    """Заказчик видит свои заявки. Эксперт — назначенные ему, заявки своей аудиторской
    группы и новые, которые он вправе взять."""

    if user.role == UserRole.CUSTOMER:
        return expertise.customer_id == user.id

    if expertise.expert_id == user.id or in_team(expertise, user):
        return True

    return expertise.expert_id is None and executor_fits(expertise, certificates, audit_lead)
