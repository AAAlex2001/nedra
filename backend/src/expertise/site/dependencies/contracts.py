"""Подготовка и подтверждение договора."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.contracts.contract_files import ContractFiles
from src.contracts.repositories.contracts import ContractRepository
from src.core.database import get_session
from src.core.file_storage import FileStorage
from src.core.settings import Settings, get_settings
from src.expertise.repositories.expertise_contract_details import (
    ExpertiseContractDetailsRepository,
)
from src.expertise.repositories.expertise_documents import ExpertiseDocumentRepository
from src.expertise.repositories.expertises import ExpertiseRepository
from src.expertise.site.dependencies.access import get_expertise_access
from src.expertise.site.usecases.confirm_contract import ConfirmExpertiseContractUseCase
from src.expertise.site.usecases.get_contract_document import (
    GetExpertiseContractDocumentUseCase,
)
from src.expertise.site.usecases.get_expertise_contract import (
    GetExpertiseContractUseCase,
)
from src.notifications.repositories.notifications import NotificationRepository
from src.users.repositories.users import UserRepository


def get_confirm_expertise_contract_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> ConfirmExpertiseContractUseCase:
    """Подтверждение договора заказчиком."""

    return ConfirmExpertiseContractUseCase(
        session=session,
        expertises=ExpertiseRepository(session=session),
        details=ExpertiseContractDetailsRepository(session=session),
        documents=ExpertiseDocumentRepository(session=session),
        contracts=ContractRepository(session=session),
        notifications=NotificationRepository(session=session),
        files=ContractFiles(storage=FileStorage(directory=settings.private_dir)),
        settings=settings,
    )


def get_expertise_contract_document_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> GetExpertiseContractDocumentUseCase:
    """Скачивание договора и соглашения."""

    return GetExpertiseContractDocumentUseCase(
        documents=ExpertiseDocumentRepository(session=session),
        access=get_expertise_access(session=session),
        details=ExpertiseContractDetailsRepository(session=session),
        users=UserRepository(session=session),
        storage=FileStorage(directory=settings.private_dir),
        settings=settings,
    )


def get_expertise_contract_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> GetExpertiseContractUseCase:
    """Сведения о договоре."""

    return GetExpertiseContractUseCase(
        access=get_expertise_access(session=session),
        contracts=ContractRepository(session=session),
    )
