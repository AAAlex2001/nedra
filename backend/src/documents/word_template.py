"""Заполнение шаблонов Word."""

from docx.document import Document
from docx.table import Table
from docx.text.paragraph import Paragraph


def table_paragraphs(*, table: Table) -> list[Paragraph]:
    """Получить абзацы таблицы и вложенных таблиц."""

    paragraphs = []

    for row in table.rows:
        for cell in row.cells:
            paragraphs.extend(cell.paragraphs)

            for nested_table in cell.tables:
                paragraphs.extend(table_paragraphs(table=nested_table))

    return paragraphs


def fill_word_template(
    *,
    document: Document,
    values: dict[str, str],
) -> None:
    """Подставить значения в метки шаблона."""

    paragraphs = list(document.paragraphs)

    for table in document.tables:
        paragraphs.extend(table_paragraphs(table=table))

    for section in document.sections:
        paragraphs.extend(section.header.paragraphs)
        paragraphs.extend(section.footer.paragraphs)

    for paragraph in paragraphs:
        for run in paragraph.runs:
            if "{{" not in run.text:
                continue

            text = run.text

            for name, value in values.items():
                text = text.replace(f"{{{{{name}}}}}", value)

            run.text = text
