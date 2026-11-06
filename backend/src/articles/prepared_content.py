"""Результат обработки текста."""

from dataclasses import dataclass

import nh3
from bs4 import BeautifulSoup
from slugify import slugify

from src.articles.options import (
    ALLOWED_HTML_ATTRIBUTES,
    ALLOWED_HTML_TAGS,
    HEADING_ANCHOR_MAX_LENGTH,
)


@dataclass(kw_only=True)
class PreparedContent:
    """Текст и оглавление."""

    html: str  # Безопасная разметка.
    headings: list[dict[str, str]]  # Заголовки и якоря.

    @classmethod
    def from_html(cls, *, raw_html: str) -> "PreparedContent":
        """Очистить текст и добавить якоря заголовков."""

        clean_html = nh3.clean(
            raw_html,
            tags=ALLOWED_HTML_TAGS,
            attributes=ALLOWED_HTML_ATTRIBUTES,
            link_rel="noopener noreferrer",
        )
        document = BeautifulSoup(clean_html, "html.parser")
        headings = []
        used_anchors = set()

        for heading in document.find_all("h2"):
            title = heading.get_text(" ", strip=True)

            if not title:
                continue

            anchor = cls._create_heading_anchor(
                title=title,
                used_anchors=used_anchors,
            )
            used_anchors.add(anchor)
            heading["id"] = anchor
            headings.append({"id": anchor, "title": title})

        return cls(
            html=str(document),
            headings=headings,
        )

    @staticmethod
    def _create_heading_anchor(
        *,
        title: str,
        used_anchors: set[str],
    ) -> str:
        """Подобрать свободный якорь."""

        base_anchor = slugify(title, max_length=HEADING_ANCHOR_MAX_LENGTH) or "section"
        anchor = base_anchor
        suffix = 2

        while anchor in used_anchors:
            anchor = f"{base_anchor}-{suffix}"
            suffix += 1

        return anchor
