"""Репозиторий экспертиз: только запросы к таблицам expertises и expertise_documents."""

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expert import ExpertCertificate
from app.models.expertise import Expertise, ExpertiseDocument, ExpertiseStatus


class ExpertiseRepository:
    """Доступ к экспертизам. Сессию получает снаружи, коммитит сам."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, expertise_id: int) -> Expertise | None:
        """Экспертиза по id или None."""

        return await self.db.get(Expertise, expertise_id)

    async def get_by_payment_id(self, payment_id: int) -> Expertise | None:
        """Экспертиза, к которой относится платёж: аванс или остаток."""

        stmt = select(Expertise).where(
            or_(
                Expertise.advance_payment_id == payment_id,
                Expertise.final_payment_id == payment_id,
            )
        )
        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def list_all(self) -> list[Expertise]:
        """Все заявки для админки, новые первыми."""

        stmt = select(Expertise).order_by(Expertise.created_at.desc())
        result = await self.db.execute(stmt)

        return list(result.scalars().all())

    async def remove(self, expertise: Expertise) -> None:
        """Удалить заявку. Документы и замечания уйдут каскадом."""

        await self.db.delete(expertise)
        await self.db.commit()

    async def list_for_customer(self, customer_id: int) -> list[Expertise]:
        """Экспертизы заказчика, новые первыми."""

        stmt = (
            select(Expertise)
            .where(Expertise.customer_id == customer_id)
            .order_by(Expertise.created_at.desc())
        )
        result = await self.db.execute(stmt)

        return list(result.scalars().all())

    async def list_for_expert(self, expert_id: int) -> list[Expertise]:
        """Экспертизы, которые эксперт взял в работу, новые первыми."""

        stmt = (
            select(Expertise)
            .where(Expertise.expert_id == expert_id)
            .order_by(Expertise.created_at.desc())
        )
        result = await self.db.execute(stmt)

        return list(result.scalars().all())

    async def list_incoming(
        self,
        certificates: list[ExpertCertificate],
        object_code: str | None,
        area_code: str | None,
    ) -> list[Expertise]:
        """Новые заявки без эксперта, подходящие под удостоверения эксперта.

        Удостоверение подходит, если совпадают объект и область, а категория
        эксперта не хуже требуемой: 1 — самая высокая, поэтому сравниваем «меньше или равно».
        Фильтры object_code и area_code сужают выдачу для кабинета.
        """

        matching: list[Expertise] = []

        stmt = (
            select(Expertise)
            .where(Expertise.status == ExpertiseStatus.NEW, Expertise.expert_id.is_(None))
            .order_by(Expertise.created_at.desc())
        )
        if object_code:
            stmt = stmt.where(Expertise.object_code == object_code)
        if area_code:
            stmt = stmt.where(Expertise.area_code == area_code)

        result = await self.db.execute(stmt)

        for expertise in result.scalars().all():
            if certificate_fits(certificates, expertise):
                matching.append(expertise)

        return matching

    async def get_document(self, expertise_id: int, document_id: int) -> ExpertiseDocument | None:
        """Документ по id, только если принадлежит этой экспертизе."""

        stmt = select(ExpertiseDocument).where(
            ExpertiseDocument.id == document_id,
            ExpertiseDocument.expertise_id == expertise_id,
        )
        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def add(self, expertise: Expertise) -> Expertise:
        """Сохранить новую экспертизу вместе с документами и уведомлениями в сессии."""

        self.db.add(expertise)
        await self.db.commit()
        await self.db.refresh(expertise)

        return expertise

    async def save(self, expertise: Expertise) -> Expertise:
        """Сохранить изменения экспертизы и всё, что сценарий добавил в сессию."""

        await self.db.commit()
        await self.db.refresh(expertise)

        return expertise


def certificate_fits(certificates: list[ExpertCertificate], expertise: Expertise) -> bool:
    """Есть ли у эксперта удостоверение под эту экспертизу."""

    for certificate in certificates:
        same_pair = (
            certificate.object_code == expertise.object_code
            and certificate.area_code == expertise.area_code
        )
        if same_pair and certificate.category <= expertise.expert_category:
            return True

    return False
