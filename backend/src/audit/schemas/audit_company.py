"""Реквизиты заказчика в ответе."""

from pydantic import BaseModel

from src.audit.models.audit_company import AuditCompany


class AuditCompanyResponse(BaseModel):
    """Сохранённые реквизиты организации."""

    full_name: str
    name: str
    inn: str
    kpp: str | None
    ogrn: str
    address: str
    bank: str
    bic: str
    account: str
    corr_account: str
    signer_position: str
    signer_name: str
    signer_genitive: str
    signer_basis: str

    @classmethod
    def from_model(cls, *, company: AuditCompany) -> "AuditCompanyResponse":
        """Подготовить реквизиты заказчика."""

        return cls(
            full_name=company.full_name,
            name=company.name,
            inn=company.inn,
            kpp=company.kpp,
            ogrn=company.ogrn,
            address=company.address,
            bank=company.bank,
            bic=company.bic,
            account=company.account,
            corr_account=company.corr_account,
            signer_position=company.signer_position,
            signer_name=company.signer_name,
            signer_genitive=company.signer_genitive,
            signer_basis=company.signer_basis,
        )
