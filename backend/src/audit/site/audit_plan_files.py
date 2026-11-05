"""Создание и хранение программы аудита."""

import asyncio
from datetime import datetime

from src.audit.options import AUDIT_PLANS_FOLDER
from src.audit.site.audit_plan_data import AuditPlanData
from src.audit.site.documents.audit_plan_document import create_audit_plan_document
from src.audit.site.schemas.audit_plan import AuditPlanResponse
from src.core.file_storage import FileStorage
from src.core.stored_file import StoredFile
from src.documents.options import DOCX_CONTENT_TYPE


class AuditPlanFiles:
    """Файлы программы аудита."""

    def __init__(self, *, storage: FileStorage) -> None:
        """Закрытое хранилище."""

        self.storage = storage

    async def save(
        self,
        *,
        plan_details: AuditPlanData,
        plan: AuditPlanResponse,
        generated_at: datetime,
    ) -> StoredFile:
        """Создать и сохранить программу аудита."""

        content = await asyncio.to_thread(
            create_audit_plan_document,
            plan_details=plan_details,
            plan=plan,
            generated_at=generated_at,
        )

        return await self.storage.save_bytes(
            content=content,
            folder=AUDIT_PLANS_FOLDER,
            original_name=f"Программа аудита — заявка {plan_details.audit_id}, версия {plan.version}.docx",
            content_type=DOCX_CONTENT_TYPE,
            extension=".docx",
        )

    async def remove_failed(self, *, document: StoredFile) -> None:
        """Удалить документ несохранённого плана."""

        await self.storage.remove_failed_upload(relative_path=document.path)
