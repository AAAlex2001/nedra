"""Подбор эксперта по удостоверениям."""

from datetime import date

from src.expertise.models.expertise import Expertise
from src.users.models.expert_certificate import ExpertCertificate


def expert_qualifies(
    *,
    expertise: Expertise,
    certificates: list[ExpertCertificate],
) -> bool:
    """Проверить аттестацию для экспертизы."""

    today = date.today()

    for certificate in certificates:
        if certificate.valid_until < today:
            continue

        if expertise.object_code is not None and certificate.object_code != expertise.object_code:
            continue

        if expertise.area_code is not None and certificate.area_code != expertise.area_code:
            continue

        if (
            expertise.expert_category is not None
            and certificate.category > expertise.expert_category
        ):
            continue

        return True

    return False
