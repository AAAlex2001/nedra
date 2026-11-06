"""Документы и замечания."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.core.file_storage import FileStorage
from src.core.settings import Settings, get_settings
from src.expertise.repositories.expertise_documents import ExpertiseDocumentRepository
from src.expertise.repositories.expertise_remarks import ExpertiseRemarkRepository
from src.expertise.site.dependencies.access import get_expertise_access
from src.expertise.site.usecases.get_expertise_document import (
    GetExpertiseDocumentUseCase,
)
from src.expertise.site.usecases.list_expertise_documents import (
    ListExpertiseDocumentsUseCase,
)
from src.expertise.site.usecases.list_expertise_remarks import (
    ListExpertiseRemarksUseCase,
)


def get_expertise_document_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> GetExpertiseDocumentUseCase:
    """Скачивание документа."""

    return GetExpertiseDocumentUseCase(
        access=get_expertise_access(session=session),
        documents=ExpertiseDocumentRepository(session=session),
        storage=FileStorage(directory=settings.private_dir),
    )


def list_expertise_documents_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> ListExpertiseDocumentsUseCase:
    """Список документов экспертизы."""

    return ListExpertiseDocumentsUseCase(
        access=get_expertise_access(session=session),
        documents=ExpertiseDocumentRepository(session=session),
    )


def list_expertise_remarks_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> ListExpertiseRemarksUseCase:
    """Замечания эксперта."""

    return ListExpertiseRemarksUseCase(
        access=get_expertise_access(session=session),
        remarks=ExpertiseRemarkRepository(session=session),
        documents=ExpertiseDocumentRepository(session=session),
    )
