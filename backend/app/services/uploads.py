"""Сохранение загруженных изображений в каталог media."""

from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.config import get_settings

ALLOWED_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
MAX_SIZE_BYTES = 5 * 1024 * 1024
CHUNK_SIZE = 1024 * 1024


class UploadError(ValueError):
    """Файл не подходит: неверный тип или превышен размер."""


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
        await write_limited(file, target)
    except UploadError:
        target.unlink(missing_ok=True)
        raise

    return f"/media/articles/{filename}"


async def write_limited(file: UploadFile, target: Path) -> None:
    """Записать файл на диск порциями, прервавшись при превышении MAX_SIZE_BYTES."""

    written = 0

    with target.open("wb") as output:
        while True:
            chunk = await file.read(CHUNK_SIZE)
            if not chunk:
                break

            written += len(chunk)
            if written > MAX_SIZE_BYTES:
                raise UploadError("Файл больше 5 МБ")

            output.write(chunk)
