"""Чтение и изменение экспертизы."""

from datetime import date

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.expertise.models.expertise import Expertise
from src.users.models.expert_certificate import ExpertCertificate


class ExpertiseRepository:
    """Условия и этапы экспертизы."""

    def __init__(self, *, session: AsyncSession) -> None:
        """Сессия базы данных."""

        self.session = session

    async def get_by_id(self, *, expertise_id: int) -> Expertise | None:
        """Найти экспертизу по номеру."""

        return await self.session.get(Expertise, expertise_id)

    async def get_for_update(self, *, expertise_id: int) -> Expertise | None:
        """Получить экспертизу для изменения."""

        statement = select(Expertise).where(Expertise.id == expertise_id).with_for_update()
        return await self.session.scalar(statement)

    async def save(self, *, expertise: Expertise) -> None:
        """Сохранить изменения экспертизы."""

        self.session.add(expertise)
        await self.session.flush()

    async def list_for_customer(self, *, user_id: int) -> list[Expertise]:
        """Получить работы заказчика."""

        statement = (
            select(Expertise)
            .where(Expertise.customer_id == user_id)
            .order_by(Expertise.created_at.desc(), Expertise.id.desc())
        )
        query_result = await self.session.scalars(statement)
        return list(query_result)

    async def list_assigned(self, *, user_id: int) -> list[Expertise]:
        """Получить назначенные работы."""

        statement = select(Expertise).where(Expertise.expert_id == user_id)
        query_result = await self.session.scalars(
            statement.order_by(Expertise.created_at.desc(), Expertise.id.desc())
        )
        return list(query_result)

    async def list_incoming(
        self,
        *,
        user_id: int,
        object_code: str | None = None,
        area_code: str | None = None,
    ) -> list[Expertise]:
        """Получить новые подходящие работы."""

        certificate = (
            select(ExpertCertificate.id)
            .where(
                ExpertCertificate.user_id == user_id,
                ExpertCertificate.valid_until >= date.today(),
                or_(
                    Expertise.object_code.is_(None),
                    ExpertCertificate.object_code == Expertise.object_code,
                ),
                or_(
                    Expertise.area_code.is_(None),
                    ExpertCertificate.area_code == Expertise.area_code,
                ),
                or_(
                    Expertise.expert_category.is_(None),
                    ExpertCertificate.category <= Expertise.expert_category,
                ),
            )
            .exists()
        )
        statement = select(Expertise).where(
            Expertise.status == "new", Expertise.expert_id.is_(None), certificate
        )

        if object_code is not None:
            statement = statement.where(Expertise.object_code == object_code)

        if area_code is not None:
            statement = statement.where(Expertise.area_code == area_code)

        query_result = await self.session.scalars(
            statement.order_by(Expertise.created_at.desc(), Expertise.id.desc())
        )
        return list(query_result)

    async def list_all(self) -> list[Expertise]:
        """Получить работы от новых к старым."""

        statement = select(Expertise).order_by(Expertise.created_at.desc(), Expertise.id.desc())
        records = await self.session.scalars(statement)

        return list(records)

    async def delete(self, *, expertise: Expertise) -> None:
        """Удалить работу и зависимые записи."""

        await self.session.delete(expertise)
        await self.session.flush()
