"""Настройки договоров."""

from pathlib import Path

from src.contracts.enums import ContractKind
from src.documents.company_requisites import CompanyRequisites

EXPERTISE_CONTRACT_KINDS = tuple(kind for kind in ContractKind if kind != ContractKind.AUDIT)
CONTRACT_KINDS_BY_OBJECT = {
    "kl": (ContractKind.CONSERVATION, ContractKind.LIQUIDATION),
    "tp": (ContractKind.REEQUIPMENT,),
    "kl_tp": (ContractKind.CONSERVATION, ContractKind.LIQUIDATION, ContractKind.REEQUIPMENT),
    "d": (ContractKind.DECLARATION,),
    "ob": (ContractKind.JUSTIFICATION,),
}


SIBNTC_REQUISITES = CompanyRequisites(
    name="ООО «СибНТЦ «Промтехэксперт»",
    inn="4217102012",
    kpp="421701001",
    address=(
        "654005, Кемеровская область, город Новокузнецк, Центральный район, "
        "ул. Орджоникидзе, дом 20, помещение № 7"
    ),
    bank="Филиал «ЦЕНТРАЛЬНЫЙ» Банка ВТБ (ПАО) в г. Москве",
    bic="044525411",
    account="40702810837070000801",
    corr_account="30101810145250000411",
    director="Д.С. Ильчук",
    vat_rate=7,
)

CONTRACT_SUBJECTS = {
    ContractKind.JUSTIFICATION: "обоснования безопасности ОПО",
    ContractKind.REEQUIPMENT: "документации на техническое перевооружение ОПО",
    ContractKind.CONSERVATION: "документации на консервацию ОПО",
    ContractKind.LIQUIDATION: "документации на ликвидацию ОПО",
    ContractKind.DECLARATION: "декларации промышленной безопасности",
    ContractKind.AUDIT: "опасных производственных объектов",
}

MONTHS = (
    "января",
    "февраля",
    "марта",
    "апреля",
    "мая",
    "июня",
    "июля",
    "августа",
    "сентября",
    "октября",
    "ноября",
    "декабря",
)

WORKING_DAYS = ("рабочий день", "рабочих дня", "рабочих дней")

DEADLINE_DAYS = {"today": 1, "three_days": 3, "week": 5, "any": 5}

DEFAULT_DAYS = 5

CONTRACT_TEMPLATES_DIRECTORY = Path(__file__).parent / "templates"
CONTRACT_TEMPLATES = {
    "expertise": "contract_nedra.docx",
    "declaration": "contract_sibntc.docx",
    "audit": "contract_audit.docx",
}
NDA_TEMPLATES = {
    "expertise": "nda_nedra.docx",
    "declaration": "nda_sibntc.docx",
    "audit": "nda_nedra.docx",
}
SIGNED_DOCUMENT_TITLES = {"contract": "Договор", "nda": "Соглашение о конфиденциальности"}
SIGNED_DOCUMENTS_FOLDER = "signed-contracts"
