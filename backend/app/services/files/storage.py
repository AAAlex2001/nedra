"""Сохранение загруженных файлов на диск.

Публичные картинки лежат в media и раздаются как статика. Документы
экспертов и заказчиков — в закрытом каталоге private: их отдаёт только
роутер после проверки, что запрашивает владелец или админ.
"""

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

CHUNK_SIZE = 1024 * 1024
MEGABYTE = 1024 * 1024

DOCUMENT_TYPES = {
    "application/pdf": ".pdf",
    "application/msword": ".doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "image/jpeg": ".jpg",
    "image/png": ".png",
}
SIGNATURE_TYPES = {
    "application/pkcs7-signature": ".p7s",
    "application/x-pkcs7-signature": ".p7s",
    "application/pgp-signature": ".sig",
    "application/octet-stream": ".sig",
}
CONCLUSION_TYPES = {**DOCUMENT_TYPES, **SIGNATURE_TYPES}
DOCUMENT_MAX_SIZE_BYTES = 10 * MEGABYTE
DOCUMENTATION_MAX_SIZE_BYTES = 50 * MEGABYTE


class UploadError(ValueError):
    """Файл не подходит: неверный тип или превышен размер."""


@dataclass(frozen=True)
class StoredFile:
    """Что известно о сохранённом файле. path — относительно корня хранилища."""

    path: str
    original_name: str
    size: int
    content_type: str


async def write_limited(file: UploadFile, target: Path, max_size_bytes: int) -> int:
    """Записать файл на диск порциями, прервавшись при превышении лимита. Возвращает размер."""

    written = 0

    with target.open("wb") as output:
        while True:
            chunk = await file.read(CHUNK_SIZE)
            if not chunk:
                break

            written += len(chunk)
            if written > max_size_bytes:
                raise UploadError(f"Файл больше {max_size_bytes // MEGABYTE} МБ")

            output.write(chunk)

    return written


class PrivateStorage:
    """Закрытый каталог на диске. Имя файла всегда случайное, исходное хранится отдельно."""

    def __init__(self, root: Path) -> None:
        self.root = root

    async def save(
        self,
        file: UploadFile,
        folder: str,
        max_size_bytes: int = DOCUMENT_MAX_SIZE_BYTES,
        allowed_types: dict[str, str] = DOCUMENT_TYPES,
    ) -> StoredFile:
        """Сохранить файл допустимого типа в подкаталог folder. Бросает UploadError.

        По умолчанию принимаются PDF, Word и картинки. Для заключений
        передаётся CONCLUSION_TYPES, где есть ещё файлы отсоединённой ЭЦП.
        """

        content_type = file.content_type
        if content_type is None:
            raise UploadError("Не указан тип файла")

        extension = allowed_types.get(content_type)
        if extension is None:
            raise UploadError("Допустимы только PDF, Word, JPEG и PNG")

        directory = self.root / folder
        directory.mkdir(parents=True, exist_ok=True)

        filename = f"{uuid4().hex}{extension}"
        target = directory / filename

        try:
            size = await write_limited(file, target, max_size_bytes)
        except UploadError:
            target.unlink(missing_ok=True)
            raise

        return StoredFile(
            path=f"{folder}/{filename}",
            original_name=file.filename or filename,
            size=size,
            content_type=content_type,
        )

    def save_bytes(
        self, content: bytes, folder: str, original_name: str, content_type: str, extension: str
    ) -> StoredFile:
        """Сохранить документ, который собрал сам сервер, например договор."""

        directory = self.root / folder
        directory.mkdir(parents=True, exist_ok=True)

        filename = f"{uuid4().hex}{extension}"
        (directory / filename).write_bytes(content)

        return StoredFile(
            path=f"{folder}/{filename}",
            original_name=original_name,
            size=len(content),
            content_type=content_type,
        )

    def remove(self, relative_path: str) -> None:
        """Удалить файл. Если его уже нет на диске, молчим: цель достигнута."""

        try:
            self.resolve(relative_path).unlink()
        except FileNotFoundError:
            return

    def resolve(self, relative_path: str) -> Path:
        """Абсолютный путь к файлу. Путь за пределами хранилища считается ошибкой."""

        root = self.root.resolve()
        target = (root / relative_path).resolve()

        if root not in target.parents:
            raise FileNotFoundError(relative_path)

        if not target.is_file():
            raise FileNotFoundError(relative_path)

        return target
