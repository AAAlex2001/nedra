"""Очистка приложений после ошибки загрузки."""

from io import BytesIO
from pathlib import Path
from unittest.mock import AsyncMock, call

import pytest
from fastapi import UploadFile

from src.audit.site.audit_file_storage import AuditFileStorage
from src.audit.site.audit_upload_files import AuditAttachedFile
from src.core.file_exceptions import InvalidUploadError
from src.core.file_storage import FileStorage
from src.core.stored_file import StoredFile


async def test_cleanup_continues_after_one_file_cannot_be_removed(*, tmp_path: Path) -> None:
    """Удалять остальные файлы и сохранить исходную ошибку загрузки."""

    storage = FileStorage(directory=tmp_path)
    storage.save = AsyncMock(
        side_effect=[
            StoredFile(
                path="documents/first.pdf",
                original_name="first.pdf",
                size=10,
                content_type="application/pdf",
            ),
            StoredFile(
                path="documents/second.pdf",
                original_name="second.pdf",
                size=10,
                content_type="application/pdf",
            ),
            InvalidUploadError("Третий файл повреждён"),
        ]
    )
    storage.remove = AsyncMock(side_effect=[PermissionError("Первый файл занят"), None])
    files = AuditFileStorage(storage=storage)
    attachments = [
        AuditAttachedFile(file=UploadFile(file=BytesIO()), kind="audit_item", item_number=number)
        for number in (1, 2, 3)
    ]

    with pytest.raises(InvalidUploadError, match="Третий файл повреждён"):
        await files.save_all(attachments=attachments)

    assert storage.remove.await_args_list == [
        call(relative_path="documents/first.pdf"),
        call(relative_path="documents/second.pdf"),
    ]
