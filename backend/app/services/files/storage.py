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
    "image/jpeg": ".jpg",
    "image/png": ".png",
}
DOCUMENT_MAX_SIZE_BYTES = 10 * MEGABYTE


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

    async def save(self, file: UploadFile, folder: str) -> StoredFile:
        """Сохранить PDF или картинку в подкаталог folder. Бросает UploadError."""

        content_type = file.content_type
        if content_type is None:
            raise UploadError("Не указан тип файла")

        extension = DOCUMENT_TYPES.get(content_type)
        if extension is None:
            raise UploadError("Допустимы только PDF, JPEG и PNG")

        directory = self.root / folder
        directory.mkdir(parents=True, exist_ok=True)

        filename = f"{uuid4().hex}{extension}"
        target = directory / filename

        try:
            size = await write_limited(file, target, DOCUMENT_MAX_SIZE_BYTES)
        except UploadError:
            target.unlink(missing_ok=True)
            raise

        return StoredFile(
            path=f"{folder}/{filename}",
            original_name=file.filename or filename,
            size=size,
            content_type=content_type,
        )

    def resolve(self, relative_path: str) -> Path:
        """Абсолютный путь к файлу. Путь за пределами хранилища считается ошибкой."""

        root = self.root.resolve()
        target = (root / relative_path).resolve()

        if root not in target.parents:
            raise FileNotFoundError(relative_path)

        if not target.is_file():
            raise FileNotFoundError(relative_path)

        return target
