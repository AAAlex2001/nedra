"""Подготовка HTML статьи: очистка от опасной разметки и сборка оглавления."""

import nh3
from bs4 import BeautifulSoup
from slugify import slugify

ALLOWED_TAGS = {
    "p", "br", "hr",
    "h2", "h3", "h4",
    "strong", "b", "em", "i", "u", "s", "mark", "sup", "sub",
    "ul", "ol", "li",
    "a", "img", "figure", "figcaption",
    "blockquote", "code", "pre",
    "table", "thead", "tbody", "tr", "th", "td",
}

ALLOWED_ATTRIBUTES = {
    "a": {"href", "title", "target"},
    "img": {"src", "alt", "title", "width", "height"},
    "td": {"colspan", "rowspan"},
    "th": {"colspan", "rowspan"},
    "ol": {"start"},
}


def make_slug(text: str, max_length: int = 200) -> str:
    """Транслитерировать текст в slug для URL: латиница, цифры и дефисы."""

    return slugify(text, max_length=max_length) or "article"


def sanitize_html(raw: str) -> str:
    """Оставить в HTML только разрешённые теги и атрибуты.

    Убирает скрипты, инлайновые стили и обработчики событий —
    всё, что могло прийти из редактора или копипаста из Word.
    Ссылкам добавляется rel="noopener noreferrer".
    """

    return nh3.clean(
        raw,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        link_rel="noopener noreferrer",
    )


def prepare_content(raw: str) -> tuple[str, list[dict[str, str]]]:
    """Очистить HTML и собрать оглавление из заголовков H2.

    Каждому H2 проставляется id-якорь, чтобы ссылки из оглавления вели на него.
    Якоря уникальны: при совпадении текста заголовков добавляется суффикс -2, -3.
    Возвращает готовый HTML и список пунктов оглавления.
    """

    clean_html = sanitize_html(raw)
    soup = BeautifulSoup(clean_html, "html.parser")
    toc: list[dict[str, str]] = []
    used_anchors: set[str] = set()

    for heading in soup.find_all("h2"):
        title = heading.get_text(" ", strip=True)
        if not title:
            continue

        wanted_anchor = slugify(title, max_length=80) or "section"
        anchor = unique_anchor(wanted_anchor, used_anchors)
        used_anchors.add(anchor)

        heading["id"] = anchor
        toc.append({"id": anchor, "title": title})

    return str(soup), toc


def unique_anchor(base: str, used: set[str]) -> str:
    """Вернуть base, если такого якоря ещё нет, иначе base-2, base-3 и так далее."""

    anchor = base
    suffix = 2

    while anchor in used:
        anchor = f"{base}-{suffix}"
        suffix += 1

    return anchor
