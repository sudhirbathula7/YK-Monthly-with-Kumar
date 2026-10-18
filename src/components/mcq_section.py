from __future__ import annotations

from dataclasses import dataclass
import re

from reportlab.lib.enums import TA_LEFT
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph

from src.pdf.helpers import paragraph_style
from src.pdf.logo_loader import draw_logo
from src.pdf.page_setup import Rect
from src.pdf.theme import (
    BLACK,
    FONT_BOLD,
    FONT_REGULAR,
    HEADING_BLUE,
    MCQ_LEADING,
    MCQ_OPTION_SIZE,
    MCQ_QUESTION_SIZE,
    SECTION_CONTENT_GAP,
    SECTION_HEADING_HEIGHT,
    SECTION_TITLE_SIZE,
    SECTION_TOP_GAP,
)


# ============================================================
# DATA MODELS
# ============================================================

@dataclass(frozen=True)
class MCQ:
    question: str
    options: tuple[str, str, str, str]
    correct_option: str | None = None
    explanation: str | None = None


@dataclass(frozen=True)
class MCQData:
    title: str
    questions: tuple[MCQ, ...]


@dataclass(frozen=True)
class _MeasuredMCQ:
    paragraph: Paragraph
    height: float
    leading: float


# ============================================================
# SECTION TITLE
# ============================================================

def _draw_section_title(
    canvas: Canvas,
    rect: Rect,
    title: str,
) -> Rect:
    heading_rect = Rect(
        x=rect.x + 3 * mm,
        y=(
            rect.top
            - SECTION_TOP_GAP
            - SECTION_HEADING_HEIGHT
        ),
        width=rect.width - 6 * mm,
        height=SECTION_HEADING_HEIGHT,
    )

    icon_size = 4.2 * mm
    icon_gap = 1.2 * mm

    title_width = stringWidth(
        title,
        FONT_BOLD,
        SECTION_TITLE_SIZE,
    )

    group_width = (
        icon_size
        + icon_gap
        + title_width
    )

    group_left = (
        heading_rect.centre_x
        - group_width / 2
    )

    icon_rect = Rect(
        x=group_left,
        y=(
            heading_rect.centre_y
            - icon_size / 2
        ),
        width=icon_size,
        height=icon_size,
    )

    draw_logo(
        canvas=canvas,
        filename="mcqs.svg",
        rect=icon_rect,
    )

    heading_baseline = (
        heading_rect.y
        + (
            heading_rect.height
            - SECTION_TITLE_SIZE
        )
        / 2
        + 1.4
    )

    canvas.saveState()

    canvas.setFillColor(
        HEADING_BLUE,
    )

    canvas.setFont(
        FONT_BOLD,
        SECTION_TITLE_SIZE,
    )

    canvas.drawString(
        icon_rect.right + icon_gap,
        heading_baseline,
        title,
    )

    canvas.restoreState()

    return heading_rect


# ============================================================
# MCQ TEXT
# ============================================================

from xml.sax.saxutils import escape


def _option_letter(value: str | None) -> str:
    raw = str(value or "").strip().upper().strip("(). ")
    if raw in {"1", "2", "3", "4"}:
        raw = "ABCD"[int(raw) - 1]
    if raw not in {"A", "B", "C", "D"}:
        raise ValueError(f"MCQ correct answer must be A, B, C or D: {value!r}")
    return raw


def _mcq_paragraph(mcq: MCQ, index: int, width: float) -> tuple[Paragraph, float]:
    if not mcq.explanation or not mcq.explanation.strip():
        raise ValueError(f"MCQ {index} needs an explanation of the correct and incorrect options")
    answer = _option_letter(mcq.correct_option)
    lines = [f"<b>{index}. {escape(mcq.question)}</b>"]
    for letter, option in zip("ABCD", mcq.options):
        lines.append(f"{letter}. {escape(option)}")
    lines.append("")  # One blank line after the four options.
    lines.append(f"<b>Correct Answer: {answer}</b>")
    explanation = escape(mcq.explanation.strip()).replace("\r\n", "\n").replace("\n", "<br/>")
    lines.append(f"<b>Explanation:</b> {explanation}")
    style = paragraph_style(
        name=f"MCQWithExplanation{index}",
        font_name=FONT_REGULAR,
        font_size=max(9.5, float(MCQ_OPTION_SIZE)),
        leading=max(12.0, float(MCQ_LEADING)),
        text_color=BLACK,
        alignment=TA_LEFT,
    )
    style.spaceBefore = 0
    style.spaceAfter = 0
    paragraph = Paragraph("<br/>".join(lines), style)
    _, height = paragraph.wrap(width, 1000 * mm)
    return paragraph, height


def draw_mcqs(canvas: Canvas, rect: Rect, data: MCQData) -> None:
    questions = data.questions
    if not questions:
        return
    if len(questions) != 2:
        raise ValueError(f"Pro Edition requires exactly 2 MCQs, got {len(questions)}")
    heading = _draw_section_title(canvas=canvas, rect=rect, title=data.title)
    top = heading.y - SECTION_CONTENT_GAP
    bottom = rect.y + 2.5 * mm
    width = rect.width - 6 * mm
    available = top - bottom
    blocks = [_mcq_paragraph(mcq, i, width) for i, mcq in enumerate(questions, 1)]
    gap = 3 * mm
    required = sum(h for _, h in blocks) + gap
    if required > available + 0.01:
        raise ValueError(
            f"MCQ questions, answers and explanations exceed the box by "
            f"{(required - available) / mm:.1f} mm. Shorten the text; fonts will not shrink."
        )
    current_top = top
    for paragraph, height in blocks:
        paragraph.drawOn(canvas, rect.x + 3 * mm, current_top - height)
        current_top -= height + gap
