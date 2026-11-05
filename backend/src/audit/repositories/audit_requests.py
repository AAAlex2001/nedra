"""Сохранение заявок на аудит."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.enums import AuditStatus
from src.audit.models.audit import Audit
from src.audit.models.audit_application import AuditApplication
from src.audit.models.audit_company import AuditCompany
from src.audit.models.audit_document import AuditDocument
from src.audit.site.audit_file_storage import SavedAuditDocument
from src.audit.site.schemas.create_audit import CreateAuditRequest


class AuditRequestRepository:
    """Заявка на аудит и её приложения."""

    def __init__(self, *, session: AsyncSession) -> None:
        """Сессия базы данных."""

        self.session = session

    async def create(
        self,
        *,
        customer_id: int,
        payload: CreateAuditRequest,
        status: AuditStatus,
        object_name: str,
        documents: list[SavedAuditDocument],
    ) -> Audit:
        """Добавить заявку с реквизитами и документами."""

        audit = Audit(
            customer_id=customer_id,
            customer_type=payload.customer_type,
            comment=payload.comment,
            status=status,
            customer_budget=payload.price,
            negotiation_allowed=payload.details.budget.negotiation != "no",
        )
        self.session.add(audit)
        await self.session.flush()

        application = AuditApplication(
            audit_id=audit.id,
            object_name=object_name,
            details=payload.details.model_dump(mode="json"),
        )
        company = AuditCompany(
            audit_id=audit.id,
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
        self.session.add_all([application, company])

        for document in documents:
            self.session.add(
                AuditDocument(
                    audit_id=audit.id,
                    uploaded_by=customer_id,
                    kind=document.kind,
                    item_number=document.item_number,
                    file_path=document.file.path,
                    original_name=document.file.original_name,
                    size=document.file.size,
                    content_type=document.file.content_type,
                )
            )

        await self.session.flush()

        return audit
