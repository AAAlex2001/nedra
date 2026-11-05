"""Оформление PDF-документов."""

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.styles import ParagraphStyle

REGULAR = "NedraDocument"
BOLD = "NedraDocumentBold"
FONT_CANDIDATES = (
    (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ),
    ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arialbd.ttf"),
    ("/Library/Fonts/Arial.ttf", "/Library/Fonts/Arial Bold.ttf"),
)
LINE = colors.HexColor("#b9bdc7")
BODY = ParagraphStyle(
    "body",
    fontName=REGULAR,
    fontSize=9,
    leading=12,
)
BODY_RIGHT = ParagraphStyle(
    "bodyRight",
    parent=BODY,
    alignment=TA_RIGHT,
)
STRONG = ParagraphStyle(
    "strong",
    fontName=BOLD,
    fontSize=9,
    leading=12,
)
TITLE = ParagraphStyle(
    "title",
    fontName=BOLD,
    fontSize=14,
    leading=18,
    spaceAfter=6,
)
SMALL = ParagraphStyle(
    "small",
    fontName=REGULAR,
    fontSize=8,
    leading=10,
)
