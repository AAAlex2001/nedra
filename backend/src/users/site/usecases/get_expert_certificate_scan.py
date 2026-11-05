"""Просмотр ранее загруженного удостоверения."""

from pathlib import Path

from src.core.file_exceptions import InvalidUploadError
from src.core.file_storage import FileStorage
from src.users.exceptions import CertificateNotFoundError
from src.users.repositories.expert_certificates import ExpertCertificateRepository


class GetExpertCertificateScanUseCase:
    """Доступ эксперта к скану своего удостоверения."""

    def __init__(
        self,
        *,
        certificates: ExpertCertificateRepository,
        storage: FileStorage,
    ) -> None:
        """Удостоверения и хранилище."""

        self.certificates = certificates
        self.storage = storage

    async def execute(
        self,
        *,
        user_id: int,
        certificate_id: int,
    ) -> Path:
        """Найти скан своего удостоверения."""

        certificate = await self.certificates.get_for_user(
            user_id=user_id,
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

        return path
