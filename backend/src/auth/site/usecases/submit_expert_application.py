"""Подача заявки эксперта."""

import asyncio

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.enums import ApplicationStatus
from src.auth.exceptions import ExpertApplicationAlreadyPendingError
from src.auth.models.expert_application import ExpertApplication
from src.auth.passwords import hash_password
from src.auth.repositories.expert_applications import ExpertApplicationRepository
from src.auth.site.expert_application_letters import ExpertApplicationLetters
from src.auth.site.schemas.expert_application import (
    CreateExpertApplicationRequest,
    ExpertApplicationCreatedResponse,
)
from src.users.attestation_validation import validate_certificate, validate_directions
from src.users.contact_validation import normalize_email, normalize_phone
from src.users.exceptions import EmailAlreadyTakenError
from src.users.models.expert_certificate import ExpertCertificate
from src.users.repositories.users import UserRepository


class SubmitExpertApplicationUseCase:
    """Регистрация заявки будущего эксперта."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        applications: ExpertApplicationRepository,
        users: UserRepository,
        letters: ExpertApplicationLetters,
    ) -> None:
        """Заявки, пользователи и письма."""

        self.session = session
        self.applications = applications
        self.users = users
        self.letters = letters

    async def execute(
        self, *, payload: CreateExpertApplicationRequest
    ) -> ExpertApplicationCreatedResponse:
        """Подать заявку эксперта."""

        validate_directions(directions=payload.directions)

        for certificate in payload.certificates:
            validate_certificate(
                area_code=certificate.area_code,
                object_code=certificate.object_code,
                category=certificate.category,
            )

        email = normalize_email(email=payload.email)
        phone = normalize_phone(phone=payload.phone)

        if await self.users.get_by_email(email=email) is not None:
            raise EmailAlreadyTakenError()

        if await self.applications.get_pending_by_email(email=email) is not None:
            raise ExpertApplicationAlreadyPendingError()

        password_hash = await asyncio.to_thread(
            hash_password,
            password=payload.password,
        )
        application = ExpertApplication(
            email=email,
            password_hash=password_hash,
            full_name=payload.full_name,
            phone=phone,
            directions=payload.directions,
            status=ApplicationStatus.PENDING,
        )
        certificates = [
            ExpertCertificate(
                area_code=certificate_data.area_code,
                object_code=certificate_data.object_code,
                category=certificate_data.category,
                valid_until=certificate_data.valid_until,
                number=certificate_data.number,
            )
            for certificate_data in payload.certificates
        ]

        try:
            await self.applications.create(
                application=application,
                certificates=certificates,
            )
            response = ExpertApplicationCreatedResponse(
                id=application.id,
                status=ApplicationStatus.PENDING,
            )
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()

            if await self.applications.get_pending_by_email(email=email) is not None:
                raise ExpertApplicationAlreadyPendingError() from None

            raise

        await self.letters.send_application_received(application=application)

        return response
