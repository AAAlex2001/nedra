"""Скан удостоверения из заявки эксперта."""

from pathlib import Path

from src.auth.admin.exceptions import ExpertApplicationNotFoundError
from src.auth.repositories.expert_applications import ExpertApplicationRepository
from src.core.file_exceptions import InvalidUploadError
from src.core.file_storage import FileStorage
from src.users.exceptions import CertificateNotFoundError
from src.users.repositories.expert_certificates import ExpertCertificateRepository


class GetApplicationCertificateScanUseCase:
    """Просмотр скана администратором."""

    def __init__(
        self,
        *,
        applications: ExpertApplicationRepository,
        certificates: ExpertCertificateRepository,
        storage: FileStorage,
    ) -> None:
        """Заявки, удостоверения и файлы."""

        self.applications = applications
        self.certificates = certificates
        self.storage = storage

    async def execute(
        self,
        *,
        application_id: int,
        certificate_id: int,
    ) -> tuple[Path, str]:
        """Найти скан удостоверения."""

        application = await self.applications.get_by_id(application_id=application_id)

        if application is None:
            raise ExpertApplicationNotFoundError()

        certificate = await self.certificates.get_for_application(
            application_id=application_id,
            certificate_id=certificate_id,
        )

        if certificate is None or certificate.scan_path is None:
            raise CertificateNotFoundError()

        try:
            path = self.storage.resolve_path(relative_path=certificate.scan_path)
        except InvalidUploadError:
            raise CertificateNotFoundError() from None

        if not path.is_file():
            raise CertificateNotFoundError()

        return path, certificate.scan_name or path.name
