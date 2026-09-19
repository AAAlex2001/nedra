"""Кто может видеть экспертизу и её файлы."""

from app.models.expert import ExpertCertificate
from app.models.expertise import Expertise
from app.models.user import User, UserRole
from app.services.expertise.repo import certificate_fits


def can_view(expertise: Expertise, user: User, certificates: list[ExpertCertificate]) -> bool:
    """Заказчик видит свои заявки. Эксперт — назначенные ему и новые по своей аттестации."""

    if user.role == UserRole.CUSTOMER:
        return expertise.customer_id == user.id

    if expertise.expert_id == user.id:
        return True

    return expertise.expert_id is None and certificate_fits(certificates, expertise)
