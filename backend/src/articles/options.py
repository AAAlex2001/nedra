"""Настройки публикаций."""

from src.articles.models.article import Article

PUBLISHED_ARTICLE_ORDER = {
    "newest": Article.published_at.desc(),
    "oldest": Article.published_at.asc(),
    "views_desc": Article.views_count.desc(),
    "views_asc": Article.views_count.asc(),
    "likes_desc": Article.likes_count.desc(),
    "likes_asc": Article.likes_count.asc(),
    "dislikes_desc": Article.dislikes_count.desc(),
    "dislikes_asc": Article.dislikes_count.asc(),
}
ADMIN_ARTICLE_ORDER = {
    "new": Article.created_at.desc(),
    "views": Article.views_count.desc(),
    "likes": Article.likes_count.desc(),
    "dislikes": Article.dislikes_count.desc(),
}

ARTICLE_SLUG_MAX_LENGTH = 240
TAG_SLUG_MAX_LENGTH = 85
HEADING_ANCHOR_MAX_LENGTH = 80
VISITOR_COOKIE = "visitor_id"
VISITOR_COOKIE_MAX_AGE = 60 * 60 * 24 * 365
DOCUMENT_URL_PATTERN = r"^/media/articles/documents/[0-9a-f]{32}\.(pdf|doc|docx|xls|xlsx)$"
DOCUMENT_KINDS = {
    ".pdf": "pdf",
    ".doc": "word",
    ".docx": "word",
    ".xls": "excel",
    ".xlsx": "excel",
}
IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
DOCUMENT_TYPES = {
    "application/pdf": ".pdf",
    "application/msword": ".doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/vnd.ms-excel": ".xls",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
}
IMAGE_MAX_SIZE_BYTES = 5 * 1024 * 1024
DOCUMENT_MAX_SIZE_BYTES = 25 * 1024 * 1024
ALLOWED_HTML_TAGS = {
    "p",
    "br",
    "hr",
    "h2",
    "h3",
    "h4",
    "strong",
    "b",
    "em",
    "i",
    "u",
    "s",
    "mark",
    "sup",
    "sub",
    "ul",
    "ol",
    "li",
    "a",
    "img",
    "figure",
    "figcaption",
    "blockquote",
    "code",
    "pre",
    "table",
    "thead",
    "tbody",
    "tr",
    "th",
    "td",
}
ALLOWED_HTML_ATTRIBUTES = {
    "a": {"href", "title", "target"},
    "img": {"src", "alt", "title", "width", "height"},
    "td": {"colspan", "rowspan"},
    "th": {"colspan", "rowspan"},
    "ol": {"start"},
}
