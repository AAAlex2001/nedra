"""Общие настройки приложения."""

from pathlib import Path

BACKEND_DIRECTORY = Path(__file__).resolve().parents[2]
ENV_FILE = BACKEND_DIRECTORY / ".env"
UPLOAD_CHUNK_SIZE_BYTES = 1024 * 1024
ORIGINAL_FILENAME_MAX_LENGTH = 255
SMTP_TIMEOUT_SECONDS = 15
SIGNATURE_MAX_SIZE_BYTES = 10 * 1024 * 1024
WORD_DOCUMENT_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
EXCEL_DOCUMENT_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
OFFICE_ARCHIVE_TYPES = {
    WORD_DOCUMENT_TYPE: "word/document.xml",
    EXCEL_DOCUMENT_TYPE: "xl/workbook.xml",
}
SIGNATURE_CONTENT_TYPES = {
    "application/pkcs7-signature",
    "application/x-pkcs7-signature",
    "application/pgp-signature",
    "application/octet-stream",
}
