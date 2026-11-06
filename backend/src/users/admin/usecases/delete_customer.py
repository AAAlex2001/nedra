"""Удаление заказчика."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.admin.exceptions import CustomerHasActivityError, CustomerNotFoundError
from src.users.admin.options import RELATED_RECORD_SQLSTATES
from src.users.enums import UserRole
from src.users.repositories.users import UserRepository


class DeleteCustomerUseCase:
    """Удаление заказчика без истории работ."""

    def __init__(self, *, session: AsyncSession, users: UserRepository) -> None:
        """Сессия и аккаунты."""

        self.session = session
        self.users = users

    async def execute(self, *, user_id: int) -> None:
        """Удалить аккаунт заказчика."""

        user = await self.users.get_for_update(user_id=user_id)

        if user is None or user.role != UserRole.CUSTOMER:
            raise CustomerNotFoundError()

        try:
            await self.users.delete(user=user)
            await self.session.commit()
        except IntegrityError as error:
            await self.session.rollback()

            if error.orig.sqlstate in RELATED_RECORD_SQLSTATES:
                raise CustomerHasActivityError() from None

            raise
