"""Кто может видеть заявку и её файлы."""

from app.models.expert import ExpertCertificate
from app.models.expertise import Expertise
from app.models.user import User, UserRole
from app.services.expertise.repo import executor_fits


def can_view(
    expertise: Expertise, user: User, certificates: list[ExpertCertificate], auditor: bool
) -> bool:
    """Заказчик видит свои заявки. Эксперт — назначенные ему и новые, которые он вправе взять."""

    if user.role == UserRole.CUSTOMER:
        return expertise.customer_id == user.id

    if expertise.expert_id == user.id:
        return True

    return expertise.expert_id is None and executor_fits(expertise, certificates, auditor)
