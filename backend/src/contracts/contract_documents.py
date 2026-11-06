"""Договор и соглашение о конфиденциальности."""

from io import BytesIO
from typing import Literal

from docx import Document

from src.contracts.contract_terms import ContractTerms
from src.contracts.customer_template_values import (
    format_date,
    money_text,
    vat_clause,
    working_days,
)
from src.contracts.enums import ContractKind
from src.contracts.options import (
    CONTRACT_SUBJECTS,
    CONTRACT_TEMPLATES,
    CONTRACT_TEMPLATES_DIRECTORY,
    NDA_TEMPLATES,
    SIGNED_DOCUMENT_TITLES,
)
from src.documents.generated_document import GeneratedDocument
from src.documents.options import DOCX_CONTENT_TYPE
from src.documents.word_template import fill_word_template


def create_contract_document(
    *,
    document_kind: Literal["contract", "nda"],
    terms: ContractTerms,
) -> GeneratedDocument:
    """Заполнить шаблон выбранного документа."""

    template_group = "expertise"

    if terms.kind == ContractKind.DECLARATION:
        template_group = "declaration"
    elif terms.kind == ContractKind.AUDIT:
        template_group = "audit"

    templates = CONTRACT_TEMPLATES if document_kind == "contract" else NDA_TEMPLATES
    document = Document(CONTRACT_TEMPLATES_DIRECTORY / templates[template_group])
    signed_date = format_date(terms.signed_at)
    values = {
        "number": terms.number,
        "date": signed_date,
        "date_caps": signed_date.upper(),
        "subject": CONTRACT_SUBJECTS[terms.kind],
        "object_name": terms.object_name,
        "days": working_days(terms.deadline),
        "price": money_text(terms.price),
        "vat": vat_clause(terms.price, terms.vat_rate),
        **terms.customer_values,
    }
    fill_word_template(
        document=document,
        values=values,
    )
    content = BytesIO()
    document.save(content)

    return GeneratedDocument(
        content=content.getvalue(),
        filename=f"{SIGNED_DOCUMENT_TITLES[document_kind]} {terms.number}.docx",
        content_type=DOCX_CONTENT_TYPE,
    )
