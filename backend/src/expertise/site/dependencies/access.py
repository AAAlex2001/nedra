"""Общие зависимости раздела."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.expertise.repositories.expertises import ExpertiseRepository
from src.expertise.site.expertise_access import ExpertiseAccess
from src.users.repositories.expert_certificates import ExpertCertificateRepository


def get_expertise_access(*, session: AsyncSession) -> ExpertiseAccess:
    """Права просмотра экспертизы."""

    return ExpertiseAccess(
        expertises=ExpertiseRepository(session=session),
        certificates=ExpertCertificateRepository(session=session),
    )
