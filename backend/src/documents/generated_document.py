"""Документ для скачивания."""

from dataclasses import dataclass


@dataclass(
    frozen=True,
    kw_only=True,
)
class GeneratedDocument:
    """Содержимое и имя созданного файла."""

    content: bytes  # Содержимое файла.
    filename: str  # Имя для скачивания.
    content_type: str  # MIME-тип документа.
