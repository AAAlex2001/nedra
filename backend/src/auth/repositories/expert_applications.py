"""Заявки на регистрацию экспертов."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.enums import ApplicationStatus
from src.auth.models.expert_application import ExpertApplication
from src.users.models.expert_certificate import ExpertCertificate


class ExpertApplicationRepository:
    """Поиск и сохранение заявок экспертов."""

    def __init__(self, *, session: AsyncSession) -> None:
        """Сессия базы данных."""

        self.session = session

    async def get_pending_by_email(self, *, email: str) -> ExpertApplication | None:
        """Найти заявку на рассмотрении."""

        statement = (
            select(ExpertApplication)
            .where(
                ExpertApplication.email == email,
                ExpertApplication.status == ApplicationStatus.PENDING,
            )
            .order_by(ExpertApplication.id.desc())
            .limit(1)
        )
        query_result = await self.session.scalars(statement)

        return query_result.one_or_none()

    async def get_by_id(self, *, application_id: int) -> ExpertApplication | None:
        """Найти заявку по номеру."""

        return await self.session.get(ExpertApplication, application_id)

    async def get_by_user_id(self, *, user_id: int) -> ExpertApplication | None:
        """Найти заявку зарегистрированного эксперта."""

        statement = (
            select(ExpertApplication)
            .where(
                ExpertApplication.user_id == user_id,
                ExpertApplication.status == ApplicationStatus.APPROVED,
            )
            .order_by(ExpertApplication.id.desc())
            .limit(1)
        )
        query_result = await self.session.scalars(statement)

        return query_result.one_or_none()

    async def get_for_update(self, *, application_id: int) -> ExpertApplication | None:
        """Получить заявку для рассмотрения."""

        statement = (
            select(ExpertApplication)
            .where(ExpertApplication.id == application_id)
            .with_for_update()
        )
        query_result = await self.session.scalars(statement)

        return query_result.one_or_none()

    async def add(self, *, application: ExpertApplication) -> None:
        """Сохранить заявку."""

        self.session.add(application)
        await self.session.flush()

    async def create(
        self,
        *,
        application: ExpertApplication,
        certificates: list[ExpertCertificate],
    ) -> None:
        """Добавить заявку с удостоверениями."""

        self.session.add(application)
        await self.session.flush()

        for certificate in certificates:
            certificate.application_id = application.id

        self.session.add_all(certificates)
        await self.session.flush()

    async def list_all(self, *, status: ApplicationStatus | None) -> list[ExpertApplication]:
        """Получить заявки на регистрацию."""

        statement = select(ExpertApplication).order_by(ExpertApplication.id.desc())

        if status is not None:
            statement = statement.where(ExpertApplication.status == status)

        query_result = await self.session.scalars(statement)

        return list(query_result)
