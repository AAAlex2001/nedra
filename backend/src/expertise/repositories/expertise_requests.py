"""Сохранение новой экспертизы."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.contracts.enums import CustomerType
from src.expertise.models.expertise import Expertise
from src.expertise.models.expertise_company import ExpertiseCompany
from src.expertise.models.expertise_document import ExpertiseDocument
from src.expertise.models.expertise_individual import ExpertiseIndividual
from src.expertise.site.expertise_file_storage import SavedExpertiseDocument
from src.expertise.site.schemas.create_expertise import CreateExpertiseRequest


class ExpertiseRequestRepository:
    """Заявка, реквизиты и документация."""

    def __init__(self, *, session: AsyncSession) -> None:
        """Сессия базы данных."""

        self.session = session

    async def create(
        self,
        *,
        customer_id: int,
        payload: CreateExpertiseRequest,
        expert_category: int | None,
        documents: list[SavedExpertiseDocument],
    ) -> Expertise:
        """Добавить заявку с реквизитами и документами."""

        expertise = Expertise(
            customer_id=customer_id,
            customer_type=payload.customer_type,
            comment=payload.comment,
            object_name=payload.object_name,
            object_code=payload.object_code,
            area_code=payload.area_code,
            hazard_class=payload.hazard_class,
            expert_category=expert_category,
            deadline=payload.deadline,
            price=payload.price,
        )
        self.session.add(expertise)
        await self.session.flush()

        if payload.customer_type == CustomerType.INDIVIDUAL and payload.individual is not None:
            individual = ExpertiseIndividual(
                expertise_id=expertise.id,
                full_name=payload.individual.full_name,
                passport_number=payload.individual.passport_number,
                passport_issued_by=payload.individual.passport_issued_by,
                passport_issued_at=payload.individual.passport_issued_at,
                address=payload.individual.address,
            )
            self.session.add(individual)
        elif payload.company is not None:
            company = ExpertiseCompany(
                expertise_id=expertise.id,
                full_name=payload.company.full_name,
                name=payload.company.name,
                inn=payload.company.inn,
                kpp=payload.company.kpp,
                ogrn=payload.company.ogrn,
                address=payload.company.address,
                bank=payload.company.bank,
                bic=payload.company.bic,
                account=payload.company.account,
                corr_account=payload.company.corr_account,
                signer_position=payload.company.signer_position,
                signer_name=payload.company.signer_name,
                signer_genitive=payload.company.signer_genitive,
                signer_basis=payload.company.signer_basis,
            )
            self.session.add(company)

        for document in documents:
            self.session.add(
                ExpertiseDocument(
                    expertise_id=expertise.id,
                    uploaded_by=customer_id,
                    kind=document.kind,
                    file_path=document.file.path,
                    original_name=document.file.original_name,
                    size=document.file.size,
                    content_type=document.file.content_type,
                )
            )

        await self.session.flush()

        return expertise
