"""Сценарий подачи заявки эксперта."""

import asyncio

from fastapi import UploadFile

from app.models.expert import ApplicationStatus, ExpertApplication, ExpertCertificate
from app.schemas.expert import ExpertApplicationInSchema
from app.services.experts.exceptions import ApplicationAlreadyPendingError, InvalidCertificateError
from app.services.experts.repo import ExpertApplicationRepository
from app.services.experts.validators import validate_certificate, validate_directions
from app.services.files.storage import PrivateStorage
from app.services.security.passwords import hash_password
from app.services.users.exceptions import EmailAlreadyTakenError
from app.services.users.repo import UserRepository
from app.services.users.validators import normalize_email, normalize_phone, validate_password

SCANS_FOLDER = "expert-certificates"


class SubmitExpertApplicationUseCase:
    """Проверить данные по справочнику, сохранить сканы и создать заявку."""

    def __init__(
        self,
        applications: ExpertApplicationRepository,
        users: UserRepository,
        storage: PrivateStorage,
    ) -> None:
        self.applications = applications
        self.users = users
        self.storage = storage

    async def execute(
        self, data: ExpertApplicationInSchema, scans: list[UploadFile]
    ) -> ExpertApplication:
        """Создать заявку. Бросает ошибки валидации, EmailAlreadyTakenError, ApplicationAlreadyPendingError, UploadError."""

        email = normalize_email(data.email)
        phone = normalize_phone(data.phone)
        validate_password(data.password)
        validate_directions(data.directions)

        for certificate in data.certificates:
            validate_certificate(certificate.area_code, certificate.object_code, certificate.category)

            if certificate.scan_index is not None and certificate.scan_index >= len(scans):
                raise InvalidCertificateError("Скан удостоверения не приложен")

        existing_user = await self.users.get_by_email(email)
        if existing_user is not None:
            raise EmailAlreadyTakenError(f"Email {email} уже занят")

        if await self.applications.has_pending(email):
            raise ApplicationAlreadyPendingError(f"Заявка от {email} уже на рассмотрении")

        password_hash = await asyncio.to_thread(hash_password, data.password)

        application = ExpertApplication(
            email=email,
            password_hash=password_hash,
            full_name=data.full_name.strip(),
            phone=phone,
            directions=data.directions,
            status=ApplicationStatus.PENDING,
        )

        for certificate in data.certificates:
            scan_path = None
            scan_name = None

            if certificate.scan_index is not None:
                stored = await self.storage.save(scans[certificate.scan_index], SCANS_FOLDER)
                scan_path = stored.path
                scan_name = stored.original_name

            application.certificates.append(
                ExpertCertificate(
                    area_code=certificate.area_code,
                    object_code=certificate.object_code,
                    category=certificate.category,
                    valid_until=certificate.valid_until,
                    scan_path=scan_path,
                    scan_name=scan_name,
                )
            )

        return await self.applications.add(application)
