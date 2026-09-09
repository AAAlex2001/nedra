"""Рендерер методичек в PDF. Принимает модуль с функцией build()."""

import importlib
import os
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)

FONTS = r"C:\Windows\Fonts"
pdfmetrics.registerFont(TTFont("Body", os.path.join(FONTS, "arial.ttf")))
pdfmetrics.registerFont(TTFont("BodyBold", os.path.join(FONTS, "arialbd.ttf")))
pdfmetrics.registerFont(TTFont("BodyItalic", os.path.join(FONTS, "ariali.ttf")))
pdfmetrics.registerFont(TTFont("Mono", os.path.join(FONTS, "consola.ttf")))
pdfmetrics.registerFontFamily("Body", normal="Body", bold="BodyBold", italic="BodyItalic")

ACCENT = colors.HexColor(os.environ.get("ACCENT", "#c0392b"))
INK = colors.HexColor("#1a1a1a")
MUTED = colors.HexColor("#5b5b5b")
CODE_BG = colors.HexColor("#f4f4f2")
CODE_BORDER = colors.HexColor("#e0dfda")
WARN_BG = colors.HexColor("#fdf1ef")
GOOD_BG = colors.HexColor("#eef4ef")

STYLES = {
    "title": ParagraphStyle("title", fontName="BodyBold", fontSize=28, leading=33,
                            textColor=INK, spaceAfter=6),
    "subtitle": ParagraphStyle("subtitle", fontName="Body", fontSize=12, leading=17,
                               textColor=MUTED, spaceAfter=22),
    "part": ParagraphStyle("part", fontName="BodyBold", fontSize=22, leading=27,
                           textColor=ACCENT, spaceBefore=6, spaceAfter=16),
    "h1": ParagraphStyle("h1", fontName="BodyBold", fontSize=17, leading=22,
                         textColor=INK, spaceBefore=18, spaceAfter=9),
    "h2": ParagraphStyle("h2", fontName="BodyBold", fontSize=12.5, leading=16.5,
                         textColor=INK, spaceBefore=13, spaceAfter=5),
    "body": ParagraphStyle("body", fontName="Body", fontSize=10, leading=15.5,
                           textColor=INK, spaceAfter=8, alignment=TA_LEFT),
    "bullet": ParagraphStyle("bullet", fontName="Body", fontSize=10, leading=15.5,
                             textColor=INK, leftIndent=12, bulletIndent=2, spaceAfter=4),
    "code": ParagraphStyle("code", fontName="Mono", fontSize=8.1, leading=11.4,
                           textColor=INK, backColor=CODE_BG, borderColor=CODE_BORDER,
                           borderWidth=0.6, borderPadding=7, spaceBefore=4, spaceAfter=10),
    "caption": ParagraphStyle("caption", fontName="BodyItalic", fontSize=8.5, leading=12,
                              textColor=MUTED, spaceAfter=3),
    "toc": ParagraphStyle("toc", fontName="Body", fontSize=10.5, leading=17, textColor=INK),
}


def P(text, style="body"):
    return Paragraph(text, STYLES[style])


def B(text):
    return Paragraph(text, STYLES["bullet"], bulletText="•")


def C(code, caption=None):
    block = Preformatted(code.strip("\n"), STYLES["code"])
    if caption:
        return KeepTogether([Paragraph(caption, STYLES["caption"]), block])
    return block


def note(text, bg=WARN_BG):
    t = Table([[Paragraph(text, STYLES["body"])]], colWidths=[165 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 0.6, CODE_BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


def table(rows, widths):
    data = [[Paragraph(f"<b>{c}</b>", STYLES["body"]) for c in rows[0]]]
    for r in rows[1:]:
        data.append([Paragraph(c, STYLES["body"]) for c in r])
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), CODE_BG),
        ("GRID", (0, 0), (-1, -1), 0.5, CODE_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    return t


def main() -> None:
    module_name = sys.argv[1]
    out = sys.argv[2]
    footer_text = sys.argv[3]

    content = importlib.import_module(module_name)
    story = content.build(P, B, C, note, table, Spacer, PageBreak, mm, CODE_BG, GOOD_BG)

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Body", 8)
        canvas.setFillColor(MUTED)
        canvas.drawString(22 * mm, 12 * mm, footer_text)
        canvas.drawRightString(188 * mm, 12 * mm, str(doc.page))
        canvas.setStrokeColor(ACCENT)
        canvas.setLineWidth(1.2)
        canvas.line(22 * mm, 16 * mm, 188 * mm, 16 * mm)
        canvas.restoreState()

    doc = BaseDocTemplate(
        out, pagesize=A4,
        leftMargin=22 * mm, rightMargin=22 * mm,
        topMargin=20 * mm, bottomMargin=22 * mm,
        title=footer_text, author="nedra",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=footer)])
    doc.build(story)
    print("PDF:", out)


if __name__ == "__main__":
    main()
