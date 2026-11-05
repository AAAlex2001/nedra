"""Отчёт о комплектности документов аудита."""

from datetime import datetime
from io import BytesIO

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.shared import Cm, Pt

from src.audit.models.audit_document import AuditDocument
from src.audit.options import AUDIT_DOCUMENTS, AUDIT_REPORT_COLUMN_WIDTHS_CM
from src.documents.options import DOCUMENT_FONT, DOCUMENT_FONT_SIZE


def create_audit_documents_report(
    *,
    audit_id: int,
    customer_title: str,
    object_name: str | None,
    documents: list[AuditDocument],
    generated_at: datetime,
) -> bytes:
    """Создать отчёт по перечню документов."""

    filenames_by_item: dict[int, list[str]] = {}

    for attachment in documents:
        if attachment.kind == "audit_item" and attachment.item_number is not None:
            filenames_by_item.setdefault(attachment.item_number, []).append(
                attachment.original_name
            )

    document = Document()
    section = document.sections[0]
    section.orientation = WD_ORIENT.LANDSCAPE
    section.page_width, section.page_height = section.page_height, section.page_width
    section.left_margin = Cm(2)
    section.right_margin = Cm(1.5)
    document.styles["Normal"].font.name = DOCUMENT_FONT
    document.styles["Normal"].font.size = Pt(DOCUMENT_FONT_SIZE)

    document.add_heading("Отчёт о представленных документах", level=1)
    document.add_paragraph("Для проведения аудита системы управления промышленной безопасностью")
    document.add_paragraph(f"Заявка № {audit_id}")
    document.add_paragraph(f"Заказчик: {customer_title}")
    document.add_paragraph(f"Объект аудита: {object_name or '—'}")
    document.add_paragraph(f"Дата формирования: {generated_at:%d.%m.%Y %H:%M}")

    provided_count = len(filenames_by_item)
    missing_count = len(AUDIT_DOCUMENTS) - provided_count
    document.add_paragraph(
        f"Представлены документы по {provided_count} из {len(AUDIT_DOCUMENTS)} пунктов перечня, "
        f"не представлены — по {missing_count}."
    )
    table = document.add_table(
        rows=1,
        cols=4,
    )
    table.style = "Table Grid"
    headings = ("№", "Документ по перечню", "Статус", "Файлы")

    for cell, heading in zip(table.rows[0].cells, headings, strict=True):
        cell.text = heading

    for number, title in enumerate(AUDIT_DOCUMENTS, start=1):
        filenames = filenames_by_item.get(number, [])
        cells = table.add_row().cells
        cells[0].text = str(number)
        cells[1].text = title
        cells[2].text = "Представлен" if filenames else "Не представлен"
        cells[3].text = "\n".join(filenames)

    for row in table.rows:
        for cell, width in zip(row.cells, AUDIT_REPORT_COLUMN_WIDTHS_CM, strict=True):
            cell.width = Cm(width)

    revisions = [attachment for attachment in documents if attachment.kind == "revision"]

    if revisions:
        document.add_heading("Документы, присланные после замечаний", level=2)

        for attachment in revisions:
            document.add_paragraph(attachment.original_name, style="List Bullet")

    output = BytesIO()
    document.save(output)

    return output.getvalue()
