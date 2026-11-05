"""Документы и замечания."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.repositories.audit_applications import AuditApplicationRepository
from src.audit.repositories.audit_customers import AuditCustomerRepository
from src.audit.repositories.audit_documents import AuditDocumentRepository
from src.audit.repositories.audit_remarks import AuditRemarkRepository
from src.audit.repositories.audits import AuditRepository
from src.audit.site.audit_file_storage import AuditFileStorage
from src.audit.site.dependencies import get_audit_access
from src.audit.site.usecases.get_audit_document import GetAuditDocumentUseCase
from src.audit.site.usecases.get_audit_documents_report import GetAuditDocumentsReportUseCase
from src.audit.site.usecases.list_audit_documents import ListAuditDocumentsUseCase
from src.audit.site.usecases.list_audit_remarks import ListAuditRemarksUseCase
from src.audit.site.usecases.upload_audit_documents import UploadAuditDocumentsUseCase
from src.core.database import get_session
from src.core.file_storage import FileStorage
from src.core.settings import Settings, get_settings
from src.notifications.repositories.notifications import NotificationRepository
from src.users.repositories.users import UserRepository


def get_upload_audit_documents_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> UploadAuditDocumentsUseCase:
    """Загрузка документов по перечню."""

    return UploadAuditDocumentsUseCase(
        session=session,
        audits=AuditRepository(session=session),
        documents=AuditDocumentRepository(session=session),
        notifications=NotificationRepository(session=session),
        files=AuditFileStorage(storage=FileStorage(directory=settings.private_dir)),
    )


def get_audit_documents_report_usecase(
    *,
    session: AsyncSession = Depends(get_session),
) -> GetAuditDocumentsReportUseCase:
    """Отчёт о комплектности документов."""

    return GetAuditDocumentsReportUseCase(
        applications=AuditApplicationRepository(session=session),
        customers=AuditCustomerRepository(session=session),
        documents=AuditDocumentRepository(session=session),
        users=UserRepository(session=session),
        access=get_audit_access(session=session),
    )


def get_audit_document_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> GetAuditDocumentUseCase:
    """Скачивание документа."""

    return GetAuditDocumentUseCase(
        access=get_audit_access(session=session),
        documents=AuditDocumentRepository(session=session),
        storage=FileStorage(directory=settings.private_dir),
    )


def get_list_audit_documents_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> ListAuditDocumentsUseCase:
    """Список документов аудита."""

    return ListAuditDocumentsUseCase(
        access=get_audit_access(session=session),
        documents=AuditDocumentRepository(session=session),
    )


def get_list_audit_remarks_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> ListAuditRemarksUseCase:
    """Замечания руководителя."""

    return ListAuditRemarksUseCase(
        access=get_audit_access(session=session),
        remarks=AuditRemarkRepository(session=session),
        documents=AuditDocumentRepository(session=session),
    )
