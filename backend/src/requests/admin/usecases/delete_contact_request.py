"""Удаление обращения."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.requests.exceptions import ContactRequestNotFoundError
from src.requests.repositories.contact_requests import ContactRequestRepository


class DeleteContactRequestUseCase:
    """Удаление обращения администратором."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        requests: ContactRequestRepository,
    ) -> None:
        """Зависимости удаления обращения."""

        self.session = session
        self.requests = requests

    async def execute(self, *, request_id: int) -> None:
        """Удалить обращение."""

        was_deleted = await self.requests.delete(request_id=request_id)

        if not was_deleted:
            raise ContactRequestNotFoundError()

        await self.session.commit()
