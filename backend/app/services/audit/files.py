"""Файлы аудита: только PDF, электронная подпись, фото и видео.

Документы в Word и Excel аудитор не может принять как официальные, поэтому
их не принимаем вовсе. Фото и видео нужны, когда выездной этап заменяют съёмкой.
"""

from fastapi import UploadFile

from app.services.files.storage import (
    AUDIT_MAX_SIZE_BYTES,
    AUDIT_TYPES,
    AUDIT_TYPES_LABEL,
    PrivateStorage,
    StoredFile,
)


async def save_audit_file(storage: PrivateStorage, file: UploadFile, folder: str) -> StoredFile:
    """Сохранить файл аудита. Бросает UploadError, если формат не подходит."""

    return await storage.save(file, folder, AUDIT_MAX_SIZE_BYTES, AUDIT_TYPES, AUDIT_TYPES_LABEL)
