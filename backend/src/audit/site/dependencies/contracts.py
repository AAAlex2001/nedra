"""Подготовка и подтверждение договора."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.repositories.audit_contract_details import AuditContractDetailsRepository
from src.audit.repositories.audit_documents import AuditDocumentRepository
from src.audit.repositories.audits import AuditRepository
from src.audit.site.dependencies.access import get_audit_access
from src.audit.site.usecases.confirm_contract import ConfirmAuditContractUseCase
from src.audit.site.usecases.get_audit_contract import GetAuditContractUseCase
from src.audit.site.usecases.get_contract_document import (
    GetAuditContractDocumentUseCase,
)
from src.contracts.contract_files import ContractFiles
from src.contracts.repositories.contracts import ContractRepository
from src.core.database import get_session
from src.core.file_storage import FileStorage
from src.core.settings import Settings, get_settings
from src.notifications.repositories.notifications import NotificationRepository
from src.users.repositories.users import UserRepository


def get_confirm_audit_contract_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> ConfirmAuditContractUseCase:
    """Подтверждение договора заказчиком."""

    return ConfirmAuditContractUseCase(
        session=session,
        audits=AuditRepository(session=session),
        details=AuditContractDetailsRepository(session=session),
        documents=AuditDocumentRepository(session=session),
        contracts=ContractRepository(session=session),
        notifications=NotificationRepository(session=session),
        files=ContractFiles(storage=FileStorage(directory=settings.private_dir)),
        settings=settings,
    )


def get_audit_contract_document_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> GetAuditContractDocumentUseCase:
    """Скачивание договора и соглашения."""

    return GetAuditContractDocumentUseCase(
        documents=AuditDocumentRepository(session=session),
        access=get_audit_access(session=session),
        details=AuditContractDetailsRepository(session=session),
        users=UserRepository(session=session),
        storage=FileStorage(directory=settings.private_dir),
        settings=settings,
    )


def get_audit_contract_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> GetAuditContractUseCase:
    """Сведения о договоре."""

    return GetAuditContractUseCase(
        access=get_audit_access(session=session),
        contracts=ContractRepository(session=session),
    )
