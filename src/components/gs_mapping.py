"""Compact one-line GS label for the monthly question panel.

Keeps the original GSMappingItem and draw_gs_mapping interfaces used by
both existing PDF generators. The syllabus/subject metadata is not printed.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas

from src.pdf.page_setup import Rect
from src.pdf.theme import BLACK, FONT_BOLD


@dataclass(frozen=True)
class GSMappingItem:
    paper: str
    subject: str = ""
    topic: str = ""


def _short_gs_label(paper: str) -> str:
    """Accept 'GS II', 'GS Paper II', or '2'; display 'GS II'."""
    value = str(paper).strip().upper()
    match = re.search(r"(?:GS\s*(?:PAPER\s*)?)?\b(IV|III|II|I|[1-4])\b", value)
    if not match:
        raise ValueError(f"Invalid GS paper: {paper!r}; expected GS I, II, III or IV")
    numeral = match.group(1)
    numeral = {"1": "I", "2": "II", "3": "III", "4": "IV"}.get(numeral, numeral)
    return f"GS {numeral}"


def draw_gs_mapping(
    canvas: Canvas,
    rect: Rect,
    items: tuple[GSMappingItem, ...],
    compact: bool = False,
) -> None:
    """Draw only one horizontally centered GS label inside the GS sidebar."""
    if not items or rect.width <= 0 or rect.height <= 0:
        return

    label = _short_gs_label(items[0].paper)
    canvas.saveState()
    try:
        canvas.setStrokeColor(BLACK)
        canvas.setLineWidth(0.55)
        canvas.line(rect.x, rect.y + 1.5 * mm, rect.x, rect.top - 1.5 * mm)

        available_width = max(1, rect.width - 1.5 * mm)
        font_size = 8.2 if compact else 9.0
        while font_size > 5.5 and stringWidth(label, FONT_BOLD, font_size) > available_width:
            font_size -= 0.25

        canvas.setFillColor(BLACK)
        canvas.setFont(FONT_BOLD, font_size)
        canvas.drawCentredString(rect.x + rect.width / 2, rect.y + (rect.height - font_size) / 2 + 1.5, label)
    finally:
        canvas.restoreState()
