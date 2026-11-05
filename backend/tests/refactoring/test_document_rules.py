"""Расчёты и реквизиты документов."""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.articles.admin.schemas.article import ArticleDocumentRequest
from src.contracts.customer_template_values import working_days
from src.contracts.enums import ContractKind
from src.contracts.executors import get_executor_requisites
from src.contracts.options import SIBNTC_REQUISITES
from src.core.settings import Settings
from src.documents.generated_document import GeneratedDocument
from src.documents.http_response import document_response
from src.documents.money_formatting import amount_in_words, format_amount, vat_included, vat_text
from src.documents.text_formatting import format_initials
from src.payments.amounts import stage_amount
from src.payments.enums import PaymentStage


@pytest.mark.parametrize(
    ("extension", "kind"),
    [("pdf", "pdf"), ("doc", "word"), ("docx", "word"), ("xls", "excel"), ("xlsx", "excel")],
)
def test_article_attachment_keeps_document_kind(extension: str, kind: str) -> None:
    url = f"/media/articles/documents/0123456789abcdef0123456789abcdef.{extension}"
    attachment = ArticleDocumentRequest(title=" Документ ", url=url)

    assert attachment.to_record() == {"title": "Документ", "url": url, "kind": kind}


def test_article_attachment_requires_uploaded_file() -> None:
    with pytest.raises(ValidationError):
        ArticleDocumentRequest(title="Чужой файл", url="https://example.com/file.pdf")


def test_money_words_and_format() -> None:
    assert format_amount(Decimal("20000.00")) == "20 000,00"
    assert format_amount(Decimal("10000.50")) == "10 000,50"
    assert amount_in_words(Decimal("20000.00")) == "Двадцать тысяч рублей 00 копеек"
    assert (
        amount_in_words(Decimal("1234.56")) == "Одна тысяча двести тридцать четыре рубля 56 копеек"
    )
    assert amount_in_words(Decimal("0.01")) == "Ноль рублей 01 копейка"


def test_vat_is_included_in_price() -> None:
    assert vat_included(Decimal("20000.00"), 7) == Decimal("1308.41")
    assert vat_included(Decimal("12000.00"), 20) == Decimal("2000.00")
    assert vat_included(Decimal("20000.00"), 0) == Decimal("0")
    assert vat_text(Decimal("20000.00"), 7) == "В том числе НДС 7 % — 1 308,41"
    assert vat_text(Decimal("20000.00"), 0) == "Без НДС"


@pytest.mark.parametrize(
    ("price", "advance", "final"),
    [
        ("20000", "10000.00", "10000.00"),
        ("20001", "10000.50", "10000.50"),
        ("0.03", "0.02", "0.01"),
    ],
)
def test_payment_stages_preserve_total(price: str, advance: str, final: str) -> None:
    assert stage_amount(price=Decimal(price), stage=PaymentStage.ADVANCE) == Decimal(advance)
    assert stage_amount(price=Decimal(price), stage=PaymentStage.FINAL) == Decimal(final)


def test_contract_names_and_deadlines() -> None:
    assert format_initials(full_name="Иванов Иван Иванович") == "И.И. Иванов"
    assert format_initials(full_name="Иванов") == "Иванов"
    assert working_days("today") == "1 (один) рабочий день"
    assert working_days(None) == "5 (пять) рабочих дней"


def test_declaration_uses_its_executor(settings: Settings) -> None:
    assert (
        get_executor_requisites(kind=ContractKind.DECLARATION, settings=settings)
        == SIBNTC_REQUISITES
    )


def test_pdf_filename_survives_http_headers() -> None:
    response = document_response(
        document=GeneratedDocument(
            content=b"%PDF",
            filename="Счёт 2026-0001.pdf",
            content_type="application/pdf",
        ),
    )

    assert response.headers["content-disposition"] == (
        "attachment; filename*=UTF-8''%D0%A1%D1%87%D1%91%D1%82%202026-0001.pdf"
    )
