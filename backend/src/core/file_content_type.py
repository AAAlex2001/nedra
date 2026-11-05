"""Проверка содержимого загруженного файла."""

from pathlib import Path
from zipfile import BadZipFile, ZipFile

import magic
from cryptography.exceptions import UnsupportedAlgorithm
from cryptography.hazmat.primitives.serialization.pkcs7 import load_der_pkcs7_certificates

from src.core.file_exceptions import InvalidUploadError
from src.core.options import OFFICE_ARCHIVE_TYPES, SIGNATURE_CONTENT_TYPES, SIGNATURE_MAX_SIZE_BYTES


def validate_file_content_type(
    *,
    path: Path,
    content_type: str,
) -> None:
    """Сверить тип файла с его содержимым."""

    if content_type in OFFICE_ARCHIVE_TYPES:
        validate_office_archive(
            path=path,
            content_type=content_type,
        )

        return

    detected_type = magic.from_file(
        str(path),
        mime=True,
    )

    if content_type in SIGNATURE_CONTENT_TYPES:
        validate_signature_file(
            path=path,
            content_type=content_type,
            detected_type=detected_type,
        )

        return

    if detected_type != content_type:
        raise InvalidUploadError("Содержимое файла не соответствует заявленному типу")


def validate_office_archive(
    *,
    path: Path,
    content_type: str,
) -> None:
    """Проверить структуру документа Word или Excel."""

    try:
        with ZipFile(path) as archive:
            entries = set(archive.namelist())
    except BadZipFile as error:
        raise InvalidUploadError("Повреждён документ Word или Excel") from error

    document_entry = OFFICE_ARCHIVE_TYPES[content_type]

    if "[Content_Types].xml" not in entries or document_entry not in entries:
        raise InvalidUploadError("Архив не содержит заявленный документ Word или Excel")


def validate_signature_file(
    *,
    path: Path,
    content_type: str,
    detected_type: str,
) -> None:
    """Проверить формат электронной подписи."""

    if path.stat().st_size > SIGNATURE_MAX_SIZE_BYTES:
        raise InvalidUploadError("Файл электронной подписи больше 10 МБ")

    if content_type == "application/pgp-signature":
        if detected_type != "application/pgp-signature":
            raise InvalidUploadError("Ожидается подпись PGP")

        return

    if content_type == "application/octet-stream" and detected_type == "application/pgp-signature":
        return

    try:
        load_der_pkcs7_certificates(path.read_bytes())
    except (ValueError, UnsupportedAlgorithm) as error:
        raise InvalidUploadError("Ожидается файл электронной подписи PKCS7 или PGP") from error
