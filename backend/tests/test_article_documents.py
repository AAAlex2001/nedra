"""Документы, приложенные к статье: тип по расширению и проверка пути."""

import pytest
from pydantic import ValidationError

from app.schemas.article import ArticleDocumentInSchema
from app.services.articles.documents import build_documents, document_kind

FILE_ID = "0123456789abcdef0123456789abcdef"


def test_document_kind_by_extension():
    assert document_kind("/media/articles/documents/a.PDF") == "pdf"
    assert document_kind("/media/articles/documents/a.docx?v=2") == "word"
    assert document_kind("https://example.com/report.xls") == "excel"
    assert document_kind("/novosti/statya") is None


def test_build_documents_adds_kind():
    items = [
        ArticleDocumentInSchema(title="Файл запроса", url=f"/media/articles/documents/{FILE_ID}.pdf"),
        ArticleDocumentInSchema(title="Смета", url=f"/media/articles/documents/{FILE_ID}.xlsx"),
    ]

    assert build_documents(items) == [
        {"title": "Файл запроса", "url": f"/media/articles/documents/{FILE_ID}.pdf", "kind": "pdf"},
        {"title": "Смета", "url": f"/media/articles/documents/{FILE_ID}.xlsx", "kind": "excel"},
    ]


def test_document_url_must_come_from_upload():
    with pytest.raises(ValidationError):
        ArticleDocumentInSchema(title="Чужой файл", url="https://example.com/file.pdf")
