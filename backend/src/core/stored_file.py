"""Сведения о сохранённом файле."""

from dataclasses import dataclass


@dataclass(frozen=True)
class StoredFile:
    """Сохранённый файл."""

    path: str  # Путь относительно каталога хранения.
    original_name: str  # Имя файла при загрузке.
    size: int  # Размер файла в байтах.
    content_type: str  # Заявленный и проверенный тип файла.
