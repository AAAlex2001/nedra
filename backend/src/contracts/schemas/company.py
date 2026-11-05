"""Реквизиты стороны договора."""

from pydantic import BaseModel, ConfigDict, Field


class CompanyDetails(BaseModel):
    """Наименование и банковские реквизиты."""

    model_config = ConfigDict(str_strip_whitespace=True)

    full_name: str = Field(
        min_length=3,
        max_length=500,
    )
    name: str = Field(
        min_length=2,
        max_length=255,
    )
    inn: str = Field(pattern=r"^[0-9]{10}([0-9]{2})?$")
    kpp: str | None = Field(
        default=None,
        pattern=r"^[0-9]{9}$",
    )
    ogrn: str = Field(pattern=r"^[0-9]{13}([0-9]{2})?$")
    address: str = Field(
        min_length=5,
        max_length=500,
    )
    bank: str = Field(
        min_length=2,
        max_length=255,
    )
    bic: str = Field(pattern=r"^[0-9]{9}$")
    account: str = Field(pattern=r"^[0-9]{20}$")
    corr_account: str = Field(pattern=r"^[0-9]{20}$")
    signer_position: str = Field(
        min_length=2,
        max_length=255,
    )
    signer_name: str = Field(
        min_length=3,
        max_length=255,
    )
    signer_genitive: str = Field(
        min_length=3,
        max_length=500,
    )
    signer_basis: str = Field(
        default="Устава",
        min_length=2,
        max_length=255,
    )
