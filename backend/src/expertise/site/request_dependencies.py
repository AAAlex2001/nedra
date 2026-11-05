"""Подача и просмотр заявок."""

from fastapi import Depends, Form
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.contracts.repositories.contracts import ContractRepository
from src.core.database import get_session
from src.core.email_sender import EmailSender
from src.core.file_storage import FileStorage
from src.core.settings import Settings, get_settings
from src.expertise.repositories.expertise_customers import ExpertiseCustomerRepository
from src.expertise.repositories.expertise_requests import ExpertiseRequestRepository
from src.expertise.repositories.expertises import ExpertiseRepository
from src.expertise.repositories.qualified_experts import QualifiedExpertRepository
from src.expertise.site.dependencies import get_expertise_access
from src.expertise.site.expertise_file_storage import ExpertiseFileStorage
from src.expertise.site.expertise_letters import ExpertiseLetters
from src.expertise.site.schemas.create_expertise import CreateExpertiseRequest
from src.expertise.site.usecases.accept_expertise import AcceptExpertiseUseCase
from src.expertise.site.usecases.create_expertise import CreateExpertiseUseCase
from src.expertise.site.usecases.get_expertise import GetExpertiseUseCase
from src.expertise.site.usecases.get_expertise_participants import GetExpertiseParticipantsUseCase
from src.expertise.site.usecases.list_expertises import ListExpertisesUseCase
from src.notifications.repositories.notifications import NotificationRepository
from src.users.repositories.expert_certificates import ExpertCertificateRepository
from src.users.repositories.users import UserRepository


def parse_expertise_form(*, payload: str = Form()) -> CreateExpertiseRequest:
    """Прочитать заявку из формы."""

    try:
        return CreateExpertiseRequest.model_validate_json(payload)
    except ValidationError as error:
        raise RequestValidationError(
            error.errors(
                include_input=False,
                include_context=False,
            )
        ) from error


def get_create_expertise_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> CreateExpertiseUseCase:
    """Подача документации на экспертизу."""

    return CreateExpertiseUseCase(
        session=session,
        requests=ExpertiseRequestRepository(session=session),
        contracts=ContractRepository(session=session),
        experts=QualifiedExpertRepository(session=session),
        notifications=NotificationRepository(session=session),
        files=ExpertiseFileStorage(storage=FileStorage(directory=settings.private_dir)),
        letters=ExpertiseLetters(
            sender=EmailSender(settings=settings),
            cabinet_url=settings.cabinet_url,
        ),
    )


def get_expertise_usecase(*, session: AsyncSession = Depends(get_session)) -> GetExpertiseUseCase:
    """Просмотр карточки."""

    return GetExpertiseUseCase(
        access=get_expertise_access(session=session),
    )


def get_accept_expertise_usecase(
    *,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> AcceptExpertiseUseCase:
    """Принятие работы исполнителем."""

    return AcceptExpertiseUseCase(
        session=session,
        expertises=ExpertiseRepository(session=session),
        certificates=ExpertCertificateRepository(session=session),
        contracts=ContractRepository(session=session),
        letters=ExpertiseLetters(
            sender=EmailSender(settings=settings),
            cabinet_url=settings.cabinet_url,
        ),
        users=UserRepository(session=session),
        notifications=NotificationRepository(session=session),
    )


def get_list_expertises_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> ListExpertisesUseCase:
    """Списки работ пользователя."""

    return ListExpertisesUseCase(
        expertises=ExpertiseRepository(session=session),
    )


def get_expertise_participants_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> GetExpertiseParticipantsUseCase:
    """Участники экспертизы."""

    return GetExpertiseParticipantsUseCase(
        access=get_expertise_access(session=session),
        users=UserRepository(session=session),
        customers=ExpertiseCustomerRepository(session=session),
    )
