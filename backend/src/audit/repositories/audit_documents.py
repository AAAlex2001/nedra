"""Документы аудита."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.models.audit_document import AuditDocument


class AuditDocumentRepository:
    """Чтение и сохранение документов."""

    def __init__(self, *, session: AsyncSession) -> None:
        """Сессия базы данных."""

        self.session = session

    async def get(
        self,
        *,
        audit_id: int,
        document_id: int,
    ) -> AuditDocument | None:
        """Найти документ заявки."""

        statement = select(AuditDocument).where(
            AuditDocument.audit_id == audit_id,
            AuditDocument.id == document_id,
        )
        return await self.session.scalar(statement)

    async def add_many(self, *, documents: list[AuditDocument]) -> None:
        """Добавить документы."""

        self.session.add_all(documents)
        await self.session.flush()

    async def list_for_audit(self, *, audit_id: int) -> list[AuditDocument]:
        """Получить все документы аудита."""

        statement = (
            select(AuditDocument)
            .where(AuditDocument.audit_id == audit_id)
            .order_by(AuditDocument.id)
        )
        documents = await self.session.scalars(statement)

        return list(documents)

    async def list_for_remarks(self, *, audit_id: int) -> list[AuditDocument]:
        """Получить приложения к замечаниям и ответам."""

        statement = (
            select(AuditDocument)
            .where(
                AuditDocument.audit_id == audit_id,
                AuditDocument.remark_id.is_not(None),
            )
            .order_by(AuditDocument.id)
        )
        documents = await self.session.scalars(statement)

        return list(documents)

    async def get_latest_by_kind(
        self,
        *,
        audit_id: int,
        kind: str,
    ) -> AuditDocument | None:
        """Найти последний документ выбранного вида."""

        statement = (
            select(AuditDocument)
            .where(
                AuditDocument.audit_id == audit_id,
                AuditDocument.kind == kind,
            )
            .order_by(AuditDocument.id.desc())
            .limit(1)
        )

        return await self.session.scalar(statement)
