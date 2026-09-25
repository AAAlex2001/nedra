"""Сценарий подачи заявки эксперта."""

import asyncio

from app.models.expert import ApplicationStatus, ExpertApplication, ExpertCertificate
from app.schemas.expert import ExpertApplicationInSchema
from app.services.experts.exceptions import (
    ApplicationAlreadyPendingError,
    ContactsRequiredError,
    InvalidCertificateError,
)
from app.services.experts.repo import ExpertApplicationRepository
from app.services.experts.validators import validate_certificate, validate_directions
from app.services.security.passwords import hash_password
from app.services.users.exceptions import EmailAlreadyTakenError
from app.services.users.repo import UserRepository
from app.services.users.validators import normalize_email, normalize_phone, validate_password


class SubmitExpertApplicationUseCase:
    """Проверить данные по справочнику и создать заявку.

    Аккаунт эксперта появляется только после одобрения, поэтому в заявке
    нужны контакты и пароль. Email должен быть свободен: один аккаунт —
    одна роль, заказчик не может стать экспертом на том же адресе.
    """

    def __init__(
        self,
        applications: ExpertApplicationRepository,
        users: UserRepository,
    ) -> None:
        self.applications = applications
        self.users = users

    async def execute(self, data: ExpertApplicationInSchema) -> ExpertApplication:
        """Создать заявку. Бросает ошибки валидации, EmailAlreadyTakenError, ApplicationAlreadyPendingError."""

        validate_directions(data.directions)

        for certificate in data.certificates:
            validate_certificate(certificate.area_code, certificate.object_code, certificate.category)

            if not certificate.number.strip():
                raise InvalidCertificateError("Укажите номер удостоверения или регистрации в ЕРУЛ")

        application = await self.build_application(data)

        if await self.applications.has_pending(application.email):
            raise ApplicationAlreadyPendingError(f"Заявка от {application.email} уже на рассмотрении")

        for certificate in data.certificates:
            application.certificates.append(
                ExpertCertificate(
                    area_code=certificate.area_code,
                    object_code=certificate.object_code,
                    category=certificate.category,
                    valid_until=certificate.valid_until,
                    number=certificate.number.strip(),
                )
            )

        application.directions = data.directions
        application.status = ApplicationStatus.PENDING

        return await self.applications.add(application)

    async def build_application(self, data: ExpertApplicationInSchema) -> ExpertApplication:
        """Заявка с контактами будущего эксперта. Email должен быть свободен."""

        if not data.email or not data.password or not data.full_name or not data.phone:
            raise ContactsRequiredError("Укажите имя, email, телефон и пароль")

        email = normalize_email(data.email)
        phone = normalize_phone(data.phone)
        validate_password(data.password)

        existing_user = await self.users.get_by_email(email)
        if existing_user is not None:
            raise EmailAlreadyTakenError(f"Email {email} уже занят")

        password_hash = await asyncio.to_thread(hash_password, data.password)

        return ExpertApplication(
            email=email,
            password_hash=password_hash,
            full_name=data.full_name.strip(),
            phone=phone,
        )
