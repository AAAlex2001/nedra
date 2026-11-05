"""Сохранение подписанных документов."""

from src.contracts.options import SIGNED_DOCUMENTS_FOLDER
from src.core.file_storage import FileStorage
from src.core.stored_file import StoredFile
from src.documents.generated_document import GeneratedDocument


class ContractFiles:
    """Файлы договора и соглашения."""

    def __init__(self, *, storage: FileStorage) -> None:
        """Хранилище документов."""

        self.storage = storage

    async def save_all(
        self,
        *,
        documents: dict[str, GeneratedDocument],
    ) -> dict[str, StoredFile]:
        """Сохранить документы договора."""

        saved_files = {}

        try:
            for kind, document in documents.items():
                saved_files[kind] = await self.storage.save_bytes(
                    content=document.content,
                    folder=SIGNED_DOCUMENTS_FOLDER,
                    original_name=document.filename,
                    content_type=document.content_type,
                    extension=".docx",
                )
        except Exception:
            await self.remove_all(files=saved_files)
            raise

        return saved_files

    async def remove_all(self, *, files: dict[str, StoredFile]) -> None:
        """Удалить файлы после ошибки."""

        for stored_file in files.values():
            await self.storage.remove_failed_upload(relative_path=stored_file.path)
