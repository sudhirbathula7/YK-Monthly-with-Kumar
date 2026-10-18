"""Quick Facts panel for the monthly Normal Edition.

This is a new component. It does not alter the existing PDF generators.
Public interface: QuickFactsData, draw_quick_facts(canvas, rect, data).
"""
from __future__ import annotations

from dataclasses import dataclass
from xml.sax.saxutils import escape

from reportlab.lib.enums import TA_LEFT
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph

from src.pdf.helpers import paragraph_style
from src.pdf.page_setup import Rect
from src.pdf.theme import (
    BLACK, FONT_BOLD, FONT_REGULAR, HEADING_BLUE,
    SECTION_CONTENT_GAP, SECTION_HEADING_HEIGHT,
    SECTION_TITLE_SIZE, SECTION_TOP_GAP,
    QUICK_FACTS_SIZE,
)


@dataclass(frozen=True)
class QuickFactsData:
    facts: tuple[str, ...]
    title: str = "QUICK FACTS"


def draw_quick_facts(canvas: Canvas, rect: Rect, data: QuickFactsData) -> None:
    """Render exactly four source-verified facts; fail clearly on overflow."""
    if len(data.facts) != 4:
        raise ValueError(f"Quick Facts requires exactly 4 facts; received {len(data.facts)}.")
    if any(not isinstance(fact, str) or not fact.strip() for fact in data.facts):
        raise ValueError("Every Quick Fact must be a nonempty string.")

    canvas.saveState()
    try:
        heading_bottom = rect.top - SECTION_TOP_GAP - SECTION_HEADING_HEIGHT
        canvas.setFillColor(HEADING_BLUE)
        canvas.setFont(FONT_BOLD, SECTION_TITLE_SIZE)
        heading_baseline = heading_bottom + (SECTION_HEADING_HEIGHT - SECTION_TITLE_SIZE) / 2 + 1.4
        canvas.drawCentredString(rect.centre_x, heading_baseline, data.title)

        padding_x = 3 * mm
        width = rect.width - 2 * padding_x - 4 * mm
        if width <= 0:
            raise ValueError("Quick Facts panel is too narrow.")
        top = heading_bottom - SECTION_CONTENT_GAP
        bottom = rect.y + 2 * mm
        available = top - bottom
        if available <= 0:
            raise ValueError("Quick Facts panel has no usable vertical space.")

        paragraphs = []
        gap = 1.1 * mm
        # Start at the theme font size. Allow at most 0.5 pt of shrinking.
        # Line spacing always equals the selected font size + 2 pt.
        font_sizes = [
            round(QUICK_FACTS_SIZE - reduction, 2)
            for reduction in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5)
        ]
        for font_size in font_sizes:
            style = paragraph_style(
                name="QuickFactsBody", font_name=FONT_REGULAR,
                font_size=font_size, leading=font_size + 2.0,
                text_color=BLACK, alignment=TA_LEFT,
            )
            paragraphs = []
            for fact in data.facts:
                para = Paragraph(escape(fact.strip()), style)
                _, height = para.wrap(width, 10000)
                paragraphs.append((para, height))
            total = sum(height for _, height in paragraphs) + gap * (len(paragraphs) - 1)
            if total <= available:
                break
        else:
            raise ValueError("Quick Facts text exceeds its panel even after the maximum 0.5 pt shrink; shorten the facts or enlarge the panel.")

        y = top
        for paragraph, height in paragraphs:
            canvas.setFillColor(BLACK)
            canvas.circle(rect.x + padding_x + 1 * mm, y - min(height / 2, 2.4 * mm), 0.4 * mm, stroke=0, fill=1)
            y -= height
            paragraph.drawOn(canvas, rect.x + padding_x + 4 * mm, y)
            y -= gap
    finally:
        canvas.restoreState()
