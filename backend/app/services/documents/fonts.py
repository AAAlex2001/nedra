"""Шрифт для PDF. Встроенные шрифты reportlab не знают кириллицы, поэтому берём TTF.

В контейнере стоит DejaVu (ставится в Dockerfile), на машине разработчика
обычно есть Arial. Путь можно задать явно через PDF_FONT_PATH.
"""

from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from app.config import get_settings

REGULAR = "Doc"
BOLD = "Doc-Bold"

CANDIDATES = [
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arialbd.ttf"),
    ("/Library/Fonts/Arial.ttf", "/Library/Fonts/Arial Bold.ttf"),
]

registered = False


def find_font() -> tuple[str, str]:
    """Пара путей «обычный и жирный». Бросает FileNotFoundError, если шрифта нет."""

    configured = get_settings().pdf_font_path
    if configured:
        return configured, configured

    for regular, bold in CANDIDATES:
        if Path(regular).is_file():
            return regular, bold if Path(bold).is_file() else regular

    raise FileNotFoundError(
        "Не найден шрифт для PDF. Укажите путь к TTF с кириллицей в PDF_FONT_PATH"
    )


def register_fonts() -> None:
    """Зарегистрировать шрифт один раз за время работы приложения."""

    global registered

    if registered:
        return

    regular, bold = find_font()
    pdfmetrics.registerFont(TTFont(REGULAR, regular))
    pdfmetrics.registerFont(TTFont(BOLD, bold))

    registered = True
