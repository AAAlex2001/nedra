"""Скачивание созданного документа."""

from urllib.parse import quote

from fastapi import Response

from src.documents.generated_document import GeneratedDocument


def document_response(*, document: GeneratedDocument) -> Response:
    """Отдать файл с исходным именем."""

    filename = quote(document.filename)

    return Response(
        content=document.content,
        media_type=document.content_type,
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"},
    )
