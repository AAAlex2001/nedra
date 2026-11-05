"""Результат обработки текста."""

from dataclasses import dataclass


@dataclass(kw_only=True)
class PreparedContent:
    """Текст и оглавление."""

    html: str  # Безопасная разметка.
    headings: list[dict[str, str]]  # Заголовки и якоря.
