"""Ссылки на документы в тексте статьи помечаются для карточек на сайте."""

from app.services.articles.content import prepare_content
from app.services.articles.documents import document_kind


def test_document_kind_by_extension():
    assert document_kind("/media/articles/documents/a.PDF") == "pdf"
    assert document_kind("/media/articles/documents/a.docx?v=2") == "word"
    assert document_kind("https://example.com/report.xls") == "excel"
    assert document_kind("/novosti/statya") is None


def test_prepare_content_marks_only_document_links():
    raw = (
        '<p><a href="/media/articles/documents/plan.pdf" class="evil" onclick="x()">План</a></p>'
        '<p><a href="/novosti/statya">Статья</a></p>'
    )

    html, _ = prepare_content(raw)

    assert 'class="document-link"' in html
    assert 'data-kind="pdf"' in html
    assert "onclick" not in html
    assert html.count("document-link") == 1
