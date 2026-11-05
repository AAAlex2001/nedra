"""Административные сценарии работы."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.billing.repositories.invoices import InvoiceRepository
from src.contracts.repositories.contracts import ContractRepository
from src.core.database import get_session
from src.core.file_storage import FileStorage
from src.core.settings import Settings, get_settings
from src.expertise.admin.usecases.delete_expertise import DeleteExpertiseUseCase
from src.expertise.admin.usecases.list_expertises import ListAdminExpertisesUseCase
from src.expertise.admin.usecases.update_expertise import UpdateExpertiseUseCase
from src.expertise.repositories.expertise_documents import ExpertiseDocumentRepository
from src.expertise.repositories.expertise_payments import ExpertisePaymentRepository
from src.expertise.repositories.expertises import ExpertiseRepository
from src.users.repositories.users import UserRepository


def get_list_expertises_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> ListAdminExpertisesUseCase:
    """Просмотр списка работ."""

    return ListAdminExpertisesUseCase(
        expertises=ExpertiseRepository(session=session),
        users=UserRepository(session=session),
    )


def get_update_expertise_usecase(
    *,
    session: AsyncSession = Depends(get_session),
) -> UpdateExpertiseUseCase:
    """Изменение работы."""

    return UpdateExpertiseUseCase(
        session=session,
        expertises=ExpertiseRepository(session=session),
        users=UserRepository(session=session),
        contracts=ContractRepository(session=session),
    )


def get_delete_expertise_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> DeleteExpertiseUseCase:
    """Удаление работы без платёжной истории."""

    return DeleteExpertiseUseCase(
        session=session,
        expertises=ExpertiseRepository(session=session),
        documents=ExpertiseDocumentRepository(session=session),
        payments=ExpertisePaymentRepository(session=session),
        invoices=InvoiceRepository(session=session),
        storage=FileStorage(directory=settings.private_dir),
    )
