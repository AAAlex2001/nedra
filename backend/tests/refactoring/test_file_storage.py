"""Загрузка и проверка файлов."""

from io import BytesIO
from pathlib import Path
from unittest.mock import AsyncMock
from zipfile import ZipFile

import pytest
from fastapi import UploadFile
from starlette.datastructures import Headers

from src.core.file_exceptions import InvalidUploadError
from src.core.file_storage import FileStorage
from src.core.options import WORD_DOCUMENT_TYPE


def make_upload(*, content: bytes, content_type: str = "application/pdf") -> UploadFile:
    """Создать загружаемый файл."""

    return UploadFile(
        file=BytesIO(content),
        filename="исходный документ.pdf",
        headers=Headers({"content-type": content_type}),
    )


async def test_upload_at_size_limit(*, tmp_path: Path) -> None:
    """Сохранить файл на границе допустимого размера."""

    content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF\n"
    storage = FileStorage(directory=tmp_path)
    file = make_upload(content=content)
    await file.read(5)

    stored = await storage.save(
        file=file,
        folder="documents",
        max_size_bytes=len(content),
        allowed_types={"application/pdf": ".pdf"},
        types_label="PDF",
    )

    assert stored.original_name == "исходный документ.pdf"
    assert stored.size == len(content)
    assert Path(stored.path).name != stored.original_name
    assert (tmp_path / stored.path).read_bytes() == content


@pytest.mark.parametrize(
    ("content", "max_size"),
    [(b"", 100), (b"%PDF-1.4\n" + b"a" * 100, 50), (b"<html>Not a PDF</html>", 100)],
)
async def test_invalid_file_is_removed(*, tmp_path: Path, content: bytes, max_size: int) -> None:
    """Удалить пустой, слишком большой или подменённый файл."""

    storage = FileStorage(directory=tmp_path)

    with pytest.raises(InvalidUploadError):
        await storage.save(
            file=make_upload(content=content),
            folder="documents",
            max_size_bytes=max_size,
            allowed_types={"application/pdf": ".pdf"},
            types_label="PDF",
        )

    assert list((tmp_path / "documents").iterdir()) == []


async def test_declared_type_is_checked_before_reading(*, tmp_path: Path) -> None:
    """Отклонить запрещённый Content-Type до чтения файла."""

    file = make_upload(content=b"unused", content_type="text/html")
    file.read = AsyncMock()
    storage = FileStorage(directory=tmp_path)

    with pytest.raises(InvalidUploadError):
        await storage.save(
            file=file,
            folder="documents",
            max_size_bytes=100,
            allowed_types={"application/pdf": ".pdf"},
            types_label="PDF",
        )

    file.read.assert_not_awaited()
    assert list(tmp_path.iterdir()) == []


async def test_read_failure_removes_partial_file(*, tmp_path: Path) -> None:
    """Удалить незавершённый файл при ошибке чтения."""

    file = make_upload(content=b"unused")
    file.read = AsyncMock(side_effect=[b"%PDF-1.4\n", OSError("Ошибка чтения")])
    storage = FileStorage(directory=tmp_path)

    with pytest.raises(OSError, match="Ошибка чтения"):
        await storage.save(
            file=file,
            folder="documents",
            max_size_bytes=100,
            allowed_types={"application/pdf": ".pdf"},
            types_label="PDF",
        )

    assert list((tmp_path / "documents").iterdir()) == []


@pytest.mark.parametrize("relative_path", ["../outside", ".", "/outside"])
async def test_paths_outside_storage_are_rejected(*, tmp_path: Path, relative_path: str) -> None:
    """Запретить запись за пределами хранилища."""

    storage = FileStorage(directory=tmp_path)

    with pytest.raises(InvalidUploadError):
        await storage.save_bytes(
            content=b"document",
            folder=relative_path,
            original_name="document.pdf",
            content_type="application/pdf",
            extension=".pdf",
        )


@pytest.mark.parametrize(
    "document_entry", ["word/document.xml", "xl/workbook.xml", "unrelated.txt"]
)
async def test_office_archive_matches_declared_type(*, tmp_path: Path, document_entry: str) -> None:
    """Отличить Word от Excel и обычного ZIP-архива."""

    buffer = BytesIO()
    with ZipFile(buffer, "w") as archive:
        archive.writestr("[Content_Types].xml", "<Types />")
        archive.writestr(document_entry, "<document />")

    storage = FileStorage(directory=tmp_path)
    upload = make_upload(content=buffer.getvalue(), content_type=WORD_DOCUMENT_TYPE)
    arguments = {
        "file": upload,
        "folder": "documents",
        "max_size_bytes": 10000,
        "allowed_types": {WORD_DOCUMENT_TYPE: ".docx"},
        "types_label": "Word",
    }

    if document_entry == "word/document.xml":
        stored = await storage.save(**arguments)
        assert stored.path.endswith(".docx")
    else:
        with pytest.raises(InvalidUploadError):
            await storage.save(**arguments)
        assert list((tmp_path / "documents").iterdir()) == []


async def test_octet_stream_does_not_allow_arbitrary_data(*, tmp_path: Path) -> None:
    """Не принимать произвольные байты под видом подписи."""

    storage = FileStorage(directory=tmp_path)
    upload = make_upload(content=b"random data", content_type="application/octet-stream")

    with pytest.raises(InvalidUploadError):
        await storage.save(
            file=upload,
            folder="signatures",
            max_size_bytes=10000,
            allowed_types={"application/octet-stream": ".sig"},
            types_label="электронная подпись",
        )

    assert list((tmp_path / "signatures").iterdir()) == []
