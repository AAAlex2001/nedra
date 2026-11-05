"""Хранение тарифов."""

from decimal import Decimal

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.tariffs.models.tariff import Tariff


class TariffRepository:
    """Тарифы по областям и объектам."""

    def __init__(self, *, session: AsyncSession) -> None:
        """Сессия базы данных."""

        self.session = session

    async def list_all(self) -> list[Tariff]:
        """Получить тарифы по порядку кодов."""

        statement = select(Tariff).order_by(Tariff.area_code, Tariff.object_code)
        query_result = await self.session.scalars(statement)

        return list(query_result)

    async def get(
        self,
        *,
        area_code: str,
        object_code: str,
    ) -> Tariff | None:
        """Найти тариф для услуги."""

        statement = select(Tariff).where(
            Tariff.area_code == area_code,
            Tariff.object_code == object_code,
        )

        return await self.session.scalar(statement)

    async def set_price(
        self,
        *,
        area_code: str,
        object_code: str,
        price: Decimal,
    ) -> None:
        """Создать тариф или изменить цену."""

        statement = insert(Tariff).values(
            area_code=area_code,
            object_code=object_code,
            price=price,
        )
        statement = statement.on_conflict_do_update(
            constraint="uq_tariffs_area_object",
            set_={"price": price, "updated_at": func.now()},
        )
        await self.session.execute(statement)

    async def delete(
        self,
        *,
        area_code: str,
        object_code: str,
    ) -> None:
        """Удалить тариф услуги."""

        statement = delete(Tariff).where(
            Tariff.area_code == area_code,
            Tariff.object_code == object_code,
        )
        await self.session.execute(statement)
