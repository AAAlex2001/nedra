"""Хранение файлов на диске."""

import asyncio
import logging
from pathlib import Path, PureWindowsPath
from uuid import uuid4

from fastapi import UploadFile

from src.core.file_content_type import validate_file_content_type
from src.core.file_exceptions import InvalidUploadError
from src.core.options import ORIGINAL_FILENAME_MAX_LENGTH, UPLOAD_CHUNK_SIZE_BYTES
from src.core.stored_file import StoredFile


class FileStorage:
    """Файлы в заданном каталоге."""

    def __init__(self, *, directory: Path) -> None:
        """Каталог хранения файлов."""

        self.directory = directory.resolve()

    async def save(
        self,
        *,
        file: UploadFile,
        folder: str,
        max_size_bytes: int,
        allowed_types: dict[str, str],
        types_label: str,
    ) -> StoredFile:
        """Проверить и сохранить загруженный файл."""

        content_type = file.content_type

        if content_type is None:
            raise InvalidUploadError("Не указан тип файла")

        extension = allowed_types.get(content_type)

        if extension is None:
            raise InvalidUploadError(f"Допустимы только {types_label}")

        if max_size_bytes <= 0:
            raise ValueError("Лимит размера должен быть положительным")

        self.resolve_path(relative_path=folder)
        filename = f"{uuid4().hex}{extension}"
        relative_path = f"{folder}/{filename}"
        target = self.resolve_path(relative_path=relative_path)
        await asyncio.to_thread(
            target.parent.mkdir,
            parents=True,
            exist_ok=True,
        )
        await file.seek(0)
        size = 0

        output = target.open("xb")

        try:
            with output:
                while True:
                    chunk = await file.read(UPLOAD_CHUNK_SIZE_BYTES)

                    if not chunk:
                        break

                    size += len(chunk)

                    if size > max_size_bytes:
                        raise InvalidUploadError("Файл превышает допустимый размер")

                    await asyncio.to_thread(output.write, chunk)

            if size == 0:
                raise InvalidUploadError("Нельзя загрузить пустой файл")

            await asyncio.to_thread(
                validate_file_content_type,
                path=target,
                content_type=content_type,
            )
        except Exception:
            await self.remove_failed_upload(relative_path=relative_path)
            raise

        original_name = PureWindowsPath(file.filename or filename).name

        return StoredFile(
            path=relative_path,
            original_name=original_name[:ORIGINAL_FILENAME_MAX_LENGTH] or filename,
            size=size,
            content_type=content_type,
        )

    async def save_bytes(
        self,
        *,
        content: bytes,
        folder: str,
        original_name: str,
        content_type: str,
        extension: str,
    ) -> StoredFile:
        """Сохранить документ, созданный приложением."""

        if not extension.startswith(".") or not extension[1:].isalnum():
            raise ValueError("Некорректное расширение файла")

        self.resolve_path(relative_path=folder)
        relative_path = f"{folder}/{uuid4().hex}{extension}"
        target = self.resolve_path(relative_path=relative_path)
        await asyncio.to_thread(
            target.parent.mkdir,
            parents=True,
            exist_ok=True,
        )

        output = target.open("xb")

        try:
            with output:
                await asyncio.to_thread(output.write, content)
        except Exception:
            await self.remove_failed_upload(relative_path=relative_path)
            raise

        return StoredFile(
            path=relative_path,
            original_name=original_name,
            size=len(content),
            content_type=content_type,
        )

    def resolve_path(self, *, relative_path: str) -> Path:
        """Получить путь внутри хранилища."""

        path = Path(relative_path)
        windows_path = PureWindowsPath(relative_path)

        if path.is_absolute() or windows_path.drive or ".." in windows_path.parts:
            raise InvalidUploadError("Недопустимый путь к файлу")

        target = (self.directory / path).resolve()

        if target == self.directory or not target.is_relative_to(self.directory):
            raise InvalidUploadError("Недопустимый путь к файлу")

        return target

    async def remove(self, *, relative_path: str) -> None:
        """Удалить сохранённый файл."""

        target = self.resolve_path(relative_path=relative_path)
        await asyncio.to_thread(
            target.unlink,
            missing_ok=True,
        )

    async def remove_failed_upload(self, *, relative_path: str) -> None:
        """Удалить файл после неудачной загрузки."""

        try:
            await self.remove(relative_path=relative_path)
        except OSError:
            logging.getLogger(__name__).error(
                "Не удалось удалить незавершённый файл: %s",
                relative_path,
            )
