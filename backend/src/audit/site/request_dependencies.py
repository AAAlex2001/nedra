"""Подача и просмотр заявок."""

from fastapi import Depends, File, Form, UploadFile
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.repositories.audit_applications import AuditApplicationRepository
from src.audit.repositories.audit_customers import AuditCustomerRepository
from src.audit.repositories.audit_requests import AuditRequestRepository
from src.audit.repositories.audits import AuditRepository
from src.audit.site.audit_file_storage import AuditFileStorage
from src.audit.site.audit_upload_files import AuditUploadFiles
from src.audit.site.dependencies import get_audit_access, get_audit_letters
from src.audit.site.schemas.create_audit import CreateAuditRequest
from src.audit.site.usecases.accept_audit import AcceptAuditUseCase
from src.audit.site.usecases.create_audit import CreateAuditUseCase
from src.audit.site.usecases.get_audit import GetAuditUseCase
from src.audit.site.usecases.get_audit_application import GetAuditApplicationUseCase
from src.audit.site.usecases.get_audit_customer import GetAuditCustomerUseCase
from src.audit.site.usecases.list_audits import ListAuditsUseCase
from src.contracts.repositories.contracts import ContractRepository
from src.core.database import get_session
from src.core.file_storage import FileStorage
from src.core.settings import Settings, get_settings
from src.notifications.repositories.notifications import NotificationRepository
from src.users.repositories.expert_profiles import ExpertProfileRepository
from src.users.repositories.users import UserRepository


def parse_audit_form(*, payload: str = Form()) -> CreateAuditRequest:
    """Прочитать анкету из формы."""

    try:
        return CreateAuditRequest.model_validate_json(payload)
    except ValidationError as error:
        raise RequestValidationError(
            error.errors(
                include_input=False,
                include_context=False,
            )
        ) from error


def get_audit_upload_files(
    *,
    files: list[UploadFile] = File(default=[]),
    items: list[int] = Form(default=[]),
    company_card: UploadFile | None = File(default=None),
    opo_certificate: UploadFile | None = File(default=None),
    power_of_attorney: UploadFile | None = File(default=None),
    sto_file: UploadFile | None = File(default=None),
) -> AuditUploadFiles:
    """Собрать приложения из формы."""

    return AuditUploadFiles(
        documents=files,
        item_numbers=items,
        company_card=company_card,
        opo_certificate=opo_certificate,
        power_of_attorney=power_of_attorney,
        sto_file=sto_file,
    )


def get_create_audit_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> CreateAuditUseCase:
    """Подача заявки на аудит."""

    return CreateAuditUseCase(
        session=session,
        requests=AuditRequestRepository(session=session),
        contracts=ContractRepository(session=session),
        profiles=ExpertProfileRepository(session=session),
        notifications=NotificationRepository(session=session),
        files=AuditFileStorage(storage=FileStorage(directory=settings.private_dir)),
        letters=get_audit_letters(settings=settings),
    )


def get_audit_usecase(*, session: AsyncSession = Depends(get_session)) -> GetAuditUseCase:
    """Просмотр карточки."""

    return GetAuditUseCase(
        access=get_audit_access(session=session),
    )


def get_accept_audit_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> AcceptAuditUseCase:
    """Принятие работы исполнителем."""

    return AcceptAuditUseCase(
        session=session,
        audits=AuditRepository(session=session),
        profiles=ExpertProfileRepository(session=session),
        letters=get_audit_letters(settings=settings),
        users=UserRepository(session=session),
        notifications=NotificationRepository(session=session),
    )


def get_list_audits_usecase(*, session: AsyncSession = Depends(get_session)) -> ListAuditsUseCase:
    """Списки работ пользователя."""

    return ListAuditsUseCase(
        audits=AuditRepository(session=session),
        profiles=ExpertProfileRepository(session=session),
    )


def get_audit_customer_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> GetAuditCustomerUseCase:
    """Заказчик аудита."""

    return GetAuditCustomerUseCase(
        access=get_audit_access(session=session),
        customers=AuditCustomerRepository(session=session),
        users=UserRepository(session=session),
    )


def get_audit_application_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> GetAuditApplicationUseCase:
    """Анкета заказчика."""

    return GetAuditApplicationUseCase(
        access=get_audit_access(session=session),
        applications=AuditApplicationRepository(session=session),
    )
