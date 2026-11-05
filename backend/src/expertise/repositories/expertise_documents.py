"""Документы экспертизы."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.expertise.models.expertise_document import ExpertiseDocument


class ExpertiseDocumentRepository:
    """Чтение и сохранение документов."""

    def __init__(self, *, session: AsyncSession) -> None:
        """Сессия базы данных."""

        self.session = session

    async def get(
        self,
        *,
        expertise_id: int,
        document_id: int,
    ) -> ExpertiseDocument | None:
        """Найти документ заявки."""

        statement = select(ExpertiseDocument).where(
            ExpertiseDocument.expertise_id == expertise_id,
            ExpertiseDocument.id == document_id,
        )
        return await self.session.scalar(statement)

    async def add_many(self, *, documents: list[ExpertiseDocument]) -> None:
        """Добавить документы."""

        self.session.add_all(documents)
        await self.session.flush()

    async def list_for_expertise(self, *, expertise_id: int) -> list[ExpertiseDocument]:
        """Получить все документы экспертизы."""

        statement = (
            select(ExpertiseDocument)
            .where(ExpertiseDocument.expertise_id == expertise_id)
            .order_by(ExpertiseDocument.id)
        )
        documents = await self.session.scalars(statement)

        return list(documents)

    async def list_for_remarks(self, *, expertise_id: int) -> list[ExpertiseDocument]:
        """Получить приложения к замечаниям и ответам."""

        statement = (
            select(ExpertiseDocument)
            .where(
                ExpertiseDocument.expertise_id == expertise_id,
                ExpertiseDocument.remark_id.is_not(None),
            )
            .order_by(ExpertiseDocument.id)
        )
        documents = await self.session.scalars(statement)

        return list(documents)

    async def get_latest_by_kind(
        self,
        *,
        expertise_id: int,
        kind: str,
    ) -> ExpertiseDocument | None:
        """Найти последний документ выбранного вида."""

        statement = (
            select(ExpertiseDocument)
            .where(
                ExpertiseDocument.expertise_id == expertise_id,
                ExpertiseDocument.kind == kind,
            )
            .order_by(ExpertiseDocument.id.desc())
            .limit(1)
        )

        return await self.session.scalar(statement)
