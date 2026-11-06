"""Сохранение сетки тарифов."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.options import MIN_AUDIT_PRICE
from src.tariffs.admin.exceptions import InvalidTariffError
from src.tariffs.admin.schemas.save_tariffs import (
    SaveTariffsRequest,
    SaveTariffsResponse,
    TariffChange,
)
from src.tariffs.options import AUDIT_AREA_CODE, AUDIT_OBJECT_CODE
from src.tariffs.repositories.tariffs import TariffRepository
from src.users.options import AREA_BY_CODE


class SaveTariffsUseCase:
    """Изменение тарифов одной транзакцией."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        tariffs: TariffRepository,
    ) -> None:
        """Зависимости изменения тарифов."""

        self.session = session
        self.tariffs = tariffs

    async def execute(self, *, payload: SaveTariffsRequest) -> list[SaveTariffsResponse]:
        """Сохранить изменения тарифов."""

        for change in payload.items:
            self._validate_change(change=change)

        # Одинаковый порядок уменьшает взаимные блокировки параллельных сохранений.
        changes = sorted(
            payload.items,
            key=lambda change: (change.area_code, change.object_code),
        )

        for change in changes:
            if change.price is None:
                await self.tariffs.delete(
                    area_code=change.area_code,
                    object_code=change.object_code,
                )
            else:
                await self.tariffs.set_price(
                    area_code=change.area_code,
                    object_code=change.object_code,
                    price=change.price,
                )

        tariffs = await self.tariffs.list_all()
        response = [SaveTariffsResponse.from_model(tariff=tariff) for tariff in tariffs]
        await self.session.commit()

        return response

    @staticmethod
    def _validate_change(*, change: TariffChange) -> None:
        """Проверить услугу и стоимость."""

        if change.price is None:
            return

        if change.area_code == AUDIT_AREA_CODE and change.object_code == AUDIT_OBJECT_CODE:
            if change.price < MIN_AUDIT_PRICE:
                raise InvalidTariffError("Тариф на аудит — не менее 100 000 ₽")

            return

        area = AREA_BY_CODE.get(change.area_code)

        if area is None:
            raise InvalidTariffError(f"Неизвестная область аттестации: {change.area_code}")

        if change.object_code not in area.objects:
            raise InvalidTariffError("Указанный объект не входит в область аттестации")
