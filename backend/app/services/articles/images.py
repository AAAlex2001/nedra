"""Сохранение картинок статей в каталог media."""

from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.config import get_settings
from app.services.files.storage import MEGABYTE, UploadError, write_limited

ALLOWED_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
MAX_SIZE_BYTES = 5 * MEGABYTE


async def save_article_image(file: UploadFile) -> str:
    """Сохранить картинку статьи и вернуть её публичный путь вида /media/articles/....

    Имя файла заменяется на случайное, чтобы исключить перезапись и небезопасные
    имена. Файл читается порциями и удаляется, если размер превысил лимит.
    """

    content_type = file.content_type
    if content_type is None:
        raise UploadError("Не указан тип файла")

    extension = ALLOWED_TYPES.get(content_type)
    if extension is None:
        raise UploadError("Допустимы только JPEG, PNG и WebP")

    folder = Path(get_settings().media_dir) / "articles"
    folder.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid4().hex}{extension}"
    target = folder / filename

    try:
        await write_limited(file, target, MAX_SIZE_BYTES)
    except UploadError:
        target.unlink(missing_ok=True)
        raise

    return f"/media/articles/{filename}"
