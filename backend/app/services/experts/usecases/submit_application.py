"""Сценарий подачи заявки эксперта."""

import asyncio

from fastapi import UploadFile

from app.models.expert import ApplicationStatus, ExpertApplication, ExpertCertificate
from app.models.user import User
from app.schemas.expert import ExpertApplicationInSchema
from app.services.experts.exceptions import (
    AlreadyExpertError,
    ApplicationAlreadyPendingError,
    ContactsRequiredError,
    InvalidCertificateError,
)
from app.services.experts.repo import ExpertApplicationRepository, ExpertProfileRepository
from app.services.experts.validators import validate_certificate, validate_directions
from app.services.files.storage import PrivateStorage
from app.services.security.passwords import hash_password
from app.services.users.exceptions import EmailAlreadyTakenError
from app.services.users.repo import UserRepository
from app.services.users.validators import normalize_email, normalize_phone, validate_password

SCANS_FOLDER = "expert-certificates"


class SubmitExpertApplicationUseCase:
    """Проверить данные по справочнику, сохранить сканы и создать заявку.

    Заявку может подать новый человек, тогда нужны контакты и пароль,
    или уже вошедший заказчик, тогда заявка привязывается к его аккаунту.
    """

    def __init__(
        self,
        applications: ExpertApplicationRepository,
        users: UserRepository,
        profiles: ExpertProfileRepository,
        storage: PrivateStorage,
    ) -> None:
        self.applications = applications
        self.users = users
        self.profiles = profiles
        self.storage = storage

    async def execute(
        self, data: ExpertApplicationInSchema, scans: list[UploadFile], user: User | None
    ) -> ExpertApplication:
        """Создать заявку. Бросает ошибки валидации, EmailAlreadyTakenError, ApplicationAlreadyPendingError, AlreadyExpertError, UploadError."""

        validate_directions(data.directions)

        for certificate in data.certificates:
            validate_certificate(certificate.area_code, certificate.object_code, certificate.category)

            if certificate.scan_index is not None and certificate.scan_index >= len(scans):
                raise InvalidCertificateError("Скан удостоверения не приложен")

        if user is None:
            application = await self.build_for_guest(data)
        else:
            application = await self.build_for_user(user)

        if await self.applications.has_pending(application.email):
            raise ApplicationAlreadyPendingError(f"Заявка от {application.email} уже на рассмотрении")

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

        application.directions = data.directions
        application.status = ApplicationStatus.PENDING

        return await self.applications.add(application)

    async def build_for_guest(self, data: ExpertApplicationInSchema) -> ExpertApplication:
        """Заявка от нового человека: проверяем контакты и что email свободен."""

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

    async def build_for_user(self, user: User) -> ExpertApplication:
        """Заявка от вошедшего заказчика: контакты из аккаунта, профиля эксперта быть не должно."""

        profile = await self.profiles.get_by_user(user.id)
        if profile is not None:
            raise AlreadyExpertError("У аккаунта уже есть профиль эксперта")

        return ExpertApplication(
            email=user.email,
            password_hash=user.password_hash,
            full_name=user.full_name,
            phone=user.phone,
            user_id=user.id,
        )
