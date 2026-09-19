"""Репозиторий тарифов: только запросы к таблице tariffs."""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tariff import Tariff


class TariffRepository:
    """Доступ к таблице tariffs. Сессию получает снаружи, коммитит сам."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_all(self) -> list[Tariff]:
        """Все тарифы в порядке области и объекта."""

        stmt = select(Tariff).order_by(Tariff.area_code, Tariff.object_code)
        result = await self.db.execute(stmt)

        return list(result.scalars().all())

    async def get(self, area_code: str, object_code: str) -> Tariff | None:
        """Тариф для пары кодов или None."""

        stmt = select(Tariff).where(
            Tariff.area_code == area_code, Tariff.object_code == object_code
        )
        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    def set_price(self, tariff: Tariff | None, area_code: str, object_code: str, price: Decimal) -> None:
        """Обновить цену существующего тарифа или добавить новый. Без commit."""

        if tariff is None:
            self.db.add(Tariff(area_code=area_code, object_code=object_code, price=price))
        else:
            tariff.price = price

    async def remove(self, tariff: Tariff) -> None:
        """Пометить тариф на удаление. Без commit."""

        await self.db.delete(tariff)

    async def commit(self) -> None:
        """Зафиксировать пакет изменений одной транзакцией."""

        await self.db.commit()
