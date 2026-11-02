"""Документы к статьям: загрузка в media и распознавание ссылок на них в тексте."""

from pathlib import Path, PurePosixPath
from urllib.parse import urlparse
from uuid import uuid4

from fastapi import UploadFile

from app.config import get_settings
from app.services.files.storage import MEGABYTE, UploadError, write_limited

DOCUMENT_KINDS = {
    ".pdf": "pdf",
    ".doc": "word",
    ".docx": "word",
    ".xls": "excel",
    ".xlsx": "excel",
}
MAX_SIZE_BYTES = 25 * MEGABYTE


def document_kind(href: str) -> str | None:
    """Тип документа по ссылке: pdf, word или excel. Для остальных ссылок — None."""

    path = urlparse(href).path
    extension = PurePosixPath(path).suffix.lower()

    return DOCUMENT_KINDS.get(extension)


async def save_article_document(file: UploadFile) -> str:
    """Сохранить документ статьи и вернуть публичный путь вида /media/articles/documents/....

    Тип определяется по расширению: браузеры отдают для Word и Excel разные
    MIME-типы, вплоть до application/octet-stream. Имя файла заменяется на случайное.
    """

    filename = file.filename or ""
    extension = PurePosixPath(filename).suffix.lower()

    if extension not in DOCUMENT_KINDS:
        raise UploadError("Допустимы PDF, Word и Excel")

    folder = Path(get_settings().media_dir) / "articles" / "documents"
    folder.mkdir(parents=True, exist_ok=True)

    target = folder / f"{uuid4().hex}{extension}"

    try:
        await write_limited(file, target, MAX_SIZE_BYTES)
    except UploadError:
        target.unlink(missing_ok=True)
        raise

    return f"/media/articles/documents/{target.name}"
