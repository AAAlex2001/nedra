"""Кириллические шрифты PDF."""

from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from src.documents.pdf.options import BOLD, FONT_CANDIDATES, REGULAR


def register_fonts(*, configured_path: Path | None) -> None:
    """Подключить обычный и полужирный шрифты."""

    if configured_path is not None:
        regular_font_path = str(configured_path)
        bold_font_path = regular_font_path
    else:
        for regular_font_path, bold_font_path in FONT_CANDIDATES:
            if Path(regular_font_path).is_file():
                if not Path(bold_font_path).is_file():
                    bold_font_path = regular_font_path
                break
        else:
            raise FileNotFoundError("Не найден шрифт PDF: задайте PDF_FONT_PATH")

    pdfmetrics.registerFont(TTFont(REGULAR, regular_font_path))
    pdfmetrics.registerFont(TTFont(BOLD, bold_font_path))
