"""Настройки платёжных документов."""

DOCUMENTS_FOLDER = "payment-documents"
DOCUMENT_MAX_SIZE_BYTES = 50 * 1024 * 1024
DOCUMENT_TYPES_LABEL = "PDF, Word, JPEG и PNG"
DOCUMENT_TYPES = {
    "application/pdf": ".pdf",
    "application/msword": ".doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "image/jpeg": ".jpg",
    "image/png": ".png",
}
