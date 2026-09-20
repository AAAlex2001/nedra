"""Правка и удаление экспертизы администратором."""

from decimal import Decimal

from app.models.expertise import Expertise, ExpertiseStatus
from app.services.expertise.exceptions import ExpertiseNotFoundError
from app.services.expertise.repo import ExpertiseRepository
from app.services.files.storage import PrivateStorage


class UpdateExpertiseUseCase:
    """Поменять статус и стоимость заявки руками, когда стороны договорились иначе."""

    def __init__(self, expertises: ExpertiseRepository) -> None:
        self.expertises = expertises

    async def execute(
        self, expertise_id: int, status: ExpertiseStatus, price: Decimal | None
    ) -> Expertise:
        """Бросает ExpertiseNotFoundError."""

        expertise = await self.expertises.get_by_id(expertise_id)
        if expertise is None:
            raise ExpertiseNotFoundError(f"Экспертиза {expertise_id} не найдена")

        expertise.status = status
        expertise.price = price

        return await self.expertises.save(expertise)


class DeleteExpertiseUseCase:
    """Удалить заявку вместе с файлами: документацией, замечаниями и заключением.

    Строки в базе уходят каскадом, а файлы на диске надо убрать вручную,
    иначе закрытое хранилище будет расти мусором.
    """

    def __init__(self, expertises: ExpertiseRepository, storage: PrivateStorage) -> None:
        self.expertises = expertises
        self.storage = storage

    async def execute(self, expertise_id: int) -> None:
        """Бросает ExpertiseNotFoundError."""

        expertise = await self.expertises.get_by_id(expertise_id)
        if expertise is None:
            raise ExpertiseNotFoundError(f"Экспертиза {expertise_id} не найдена")

        for document in expertise.documents:
            self.storage.remove(document.file_path)

        await self.expertises.remove(expertise)
