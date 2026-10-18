from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from reportlab.lib.colors import Color, HexColor
from reportlab.lib.units import mm


# ============================================================
# COLOURS
# ============================================================

BLACK: Final[Color] = HexColor("#111827")
TEXT_BLACK: Final[Color] = HexColor("#172033")

HEADING_BLUE: Final[Color] = HexColor("#102A5C")

DARK_GREY: Final[Color] = HexColor("#4B5563")
MEDIUM_GREY: Final[Color] = HexColor("#7A8699")

LIGHT_GREY: Final[Color] = HexColor("#B8C5D8")
VERY_LIGHT_GREY: Final[Color] = HexColor("#E7ECF3")

WHITE: Final[Color] = HexColor("#FFFFFF")


# ============================================================
# COMPATIBILITY COLOURS
# ============================================================

NAVY: Final[Color] = HEADING_BLUE
DARK_NAVY: Final[Color] = HEADING_BLUE

BORDER_GREY: Final[Color] = LIGHT_GREY
LIGHT_BORDER: Final[Color] = LIGHT_GREY
DIVIDER_GREY: Final[Color] = LIGHT_GREY

ANSWER_BLUE: Final[Color] = HEADING_BLUE
LIGHT_BLUE: Final[Color] = WHITE
OFF_WHITE: Final[Color] = WHITE


# ============================================================
# FONTS
# ============================================================

FONT_REGULAR: Final[str] = "Calibri"
FONT_BOLD: Final[str] = "Calibri-Bold"
FONT_ITALIC: Final[str] = "Calibri-Italic"
FONT_BOLD_ITALIC: Final[str] = "Calibri-BoldItalic"

FONT_OBLIQUE: Final[str] = FONT_ITALIC
FONT_BOLD_OBLIQUE: Final[str] = FONT_BOLD_ITALIC


# Change only this value to adjust every font size in Normal and Pro PDFs.

FONT_ADJUSTMENT: Final[float] = 0.5

# ============================================================
# HEADER
# ============================================================

HEADER_TITLE_SIZE: Final[float] = 19 + FONT_ADJUSTMENT
HEADER_TITLE_SIZE_FULL: Final[float] = 19 + FONT_ADJUSTMENT
HEADER_TITLE_SIZE_HALF: Final[float] = 19 + FONT_ADJUSTMENT
HEADER_SUBTITLE_SIZE: Final[float] = 9 + FONT_ADJUSTMENT
HEADER_DATE_LABEL_SIZE: Final[float] = 9 + FONT_ADJUSTMENT
HEADER_DATE_SIZE: Final[float] = 9 + FONT_ADJUSTMENT
HEADER_CODE_SIZE: Final[float] = 9 + FONT_ADJUSTMENT
HEADER_RADIUS: Final[float] = 2 * mm


# ============================================================
# QUESTION
# ============================================================

QUESTION_SIZE: Final[float] = 14.0 + FONT_ADJUSTMENT
QUESTION_LEADING: Final[float] = QUESTION_SIZE + 2.0

QUESTION_SIZE_FULL: Final[float] = 14.0 + FONT_ADJUSTMENT
QUESTION_LEADING_FULL: Final[float] = QUESTION_SIZE_FULL + 2.0

QUESTION_SIZE_HALF: Final[float] = 14.0 + FONT_ADJUSTMENT
QUESTION_LEADING_HALF: Final[float] = QUESTION_SIZE_HALF + 2.0

ANCHOR_LABEL_SIZE: Final[float] = 9 + FONT_ADJUSTMENT
ANCHOR_SIZE: Final[float] = 9 + FONT_ADJUSTMENT
ANCHOR_TEXT_SIZE: Final[float] = 9 + FONT_ADJUSTMENT
ANCHOR_LEADING: Final[float] = ANCHOR_TEXT_SIZE + 2.0


# ============================================================
# SECTION TITLES
# ============================================================

SECTION_TITLE_SIZE: Final[float] = 10.5 + FONT_ADJUSTMENT
SECTION_TITLE_LEADING: Final[float] = SECTION_TITLE_SIZE + 2.0

SECTION_HEADING_SIZE_FULL: Final[float] = 10.5 + FONT_ADJUSTMENT
SECTION_HEADING_SIZE_HALF: Final[float] = 10.5 + FONT_ADJUSTMENT
# ============================================================
# SECTION SPACING
# ============================================================

# A: Top border -> section heading/icon
SECTION_TOP_GAP: Final[float] = 1.6 * mm

# B: Section heading -> first content
SECTION_CONTENT_GAP: Final[float] = 2.0 * mm

# Physical height of heading/icon area
SECTION_HEADING_HEIGHT: Final[float] = 4.2 * mm

# ============================================================
# GS MAPPING
# ============================================================

GS_PAPER_SIZE: Final[float] = 10 + FONT_ADJUSTMENT
GS_SUBJECT_SIZE: Final[float] = 9 + FONT_ADJUSTMENT
GS_TOPIC_SIZE: Final[float] = 8 + FONT_ADJUSTMENT
GS_TOPIC_LEADING: Final[float] = GS_TOPIC_SIZE + 2.0


# ============================================================
# KNOWLEDGE POINTS
# ============================================================

KNOWLEDGE_NUMBER_SIZE: Final[float] = 13 + FONT_ADJUSTMENT
KNOWLEDGE_NUMBER_SIZE_FULL: Final[float] = 13 + FONT_ADJUSTMENT
KNOWLEDGE_NUMBER_SIZE_HALF: Final[float] = 13 + FONT_ADJUSTMENT
KNOWLEDGE_HEADING_SIZE: Final[float] = 9.8 + FONT_ADJUSTMENT
KNOWLEDGE_HEADING_LEADING: Final[float] = KNOWLEDGE_HEADING_SIZE + 2.0

KNOWLEDGE_TEXT_SIZE: Final[float] = 9.5 + FONT_ADJUSTMENT
KNOWLEDGE_LEADING: Final[float] = KNOWLEDGE_TEXT_SIZE + 2.0

KNOWLEDGE_TEXT_SIZE_FULL: Final[float] = 9.5 + FONT_ADJUSTMENT
KNOWLEDGE_LEADING_FULL: Final[float] = KNOWLEDGE_TEXT_SIZE_FULL + 2.0

KNOWLEDGE_TEXT_SIZE_HALF: Final[float] = 9.5 + FONT_ADJUSTMENT
KNOWLEDGE_LEADING_HALF: Final[float] = KNOWLEDGE_TEXT_SIZE_HALF + 2.0


# ============================================================
# QUICK FACTS
# ============================================================

QUICK_FACTS_SIZE: Final[float] = 9.5 + FONT_ADJUSTMENT
QUICK_FACTS_LEADING: Final[float] = QUICK_FACTS_SIZE + 2.0
QUICK_FACTS_SIZE_FULL: Final[float] = 9.5 + FONT_ADJUSTMENT
QUICK_FACTS_LEADING_FULL: Final[float] = QUICK_FACTS_SIZE_FULL + 2.0
QUICK_FACTS_SIZE_HALF: Final[float] = 9.5 + FONT_ADJUSTMENT
QUICK_FACTS_LEADING_HALF: Final[float] = QUICK_FACTS_SIZE_HALF + 2.0

# ============================================================
# KEY TAKEAWAY
# ============================================================

TAKEAWAY_SIZE: Final[float] = 9.5 + FONT_ADJUSTMENT
TAKEAWAY_LEADING: Final[float] = TAKEAWAY_SIZE + 2.0

TAKEAWAY_SIZE_FULL: Final[float] = 9.5 + FONT_ADJUSTMENT
TAKEAWAY_LEADING_FULL: Final[float] = TAKEAWAY_SIZE_FULL + 2.0

TAKEAWAY_SIZE_HALF: Final[float] = 9.5 + FONT_ADJUSTMENT
TAKEAWAY_LEADING_HALF: Final[float] = TAKEAWAY_SIZE_HALF + 2.0


# ============================================================
# MAINS ANSWER
# ============================================================

MAINS_QUESTION_SIZE: Final[float] = 9.8 + FONT_ADJUSTMENT
MAINS_TEXT_SIZE: Final[float] = 9.5 + FONT_ADJUSTMENT
MAINS_LEADING: Final[float] = MAINS_QUESTION_SIZE + 2.0
MAINS_TEXT_LEADING: Final[float] = MAINS_TEXT_SIZE + 2.0

MAINS_WORD_NOTE_SIZE: Final[float] = 6 + FONT_ADJUSTMENT
# ============================================================
# MCQS
# ============================================================

MCQ_QUESTION_SIZE: Final[float] = 9.8 + FONT_ADJUSTMENT
MCQ_OPTION_SIZE: Final[float] = 9.5 + FONT_ADJUSTMENT
MCQ_OPTION_LEADING: Final[float] = MCQ_OPTION_SIZE + 2.0

MCQ_LEADING: Final[float] = MCQ_QUESTION_SIZE + 2.0
MCQ_ANSWER_SIZE: Final[float] = 9.5 + FONT_ADJUSTMENT
MCQ_ANSWER_LEADING: Final[float] = MCQ_ANSWER_SIZE + 2.0

# ============================================================
# FOOTER
# ============================================================

# Typography rules for section renderers.
# A renderer may shrink a font only as far as its default minus 0.5 pt.
FONT_SHRINK_MAX: Final[float] = 0.5
FONT_SHRINK_STEP: Final[float] = 0.1
LINE_SPACING_EXTRA: Final[float] = 2.0

def minimum_font_size(default_size: float) -> float:
    return round(default_size - FONT_SHRINK_MAX, 2)

def leading_for(font_size: float) -> float:
    return round(font_size + LINE_SPACING_EXTRA, 2)

QUESTION_MIN_SIZE: Final[float] = QUESTION_SIZE - FONT_SHRINK_MAX
SECTION_TITLE_MIN_SIZE: Final[float] = SECTION_TITLE_SIZE - FONT_SHRINK_MAX
KNOWLEDGE_HEADING_MIN_SIZE: Final[float] = KNOWLEDGE_HEADING_SIZE - FONT_SHRINK_MAX
KNOWLEDGE_TEXT_MIN_SIZE: Final[float] = KNOWLEDGE_TEXT_SIZE - FONT_SHRINK_MAX
QUICK_FACTS_MIN_SIZE: Final[float] = QUICK_FACTS_SIZE - FONT_SHRINK_MAX
TAKEAWAY_MIN_SIZE: Final[float] = TAKEAWAY_SIZE - FONT_SHRINK_MAX
MAINS_QUESTION_MIN_SIZE: Final[float] = MAINS_QUESTION_SIZE - FONT_SHRINK_MAX
MAINS_TEXT_MIN_SIZE: Final[float] = MAINS_TEXT_SIZE - FONT_SHRINK_MAX
MCQ_QUESTION_MIN_SIZE: Final[float] = MCQ_QUESTION_SIZE - FONT_SHRINK_MAX
MCQ_OPTION_MIN_SIZE: Final[float] = MCQ_OPTION_SIZE - FONT_SHRINK_MAX
MCQ_ANSWER_MIN_SIZE: Final[float] = MCQ_ANSWER_SIZE - FONT_SHRINK_MAX
# Render Key Takeaway using this font rather than FONT_REGULAR.
TAKEAWAY_FONT: Final[str] = FONT_BOLD

FOOTER_SIZE: Final[float] = 7 + FONT_ADJUSTMENT
# ============================================================
# BORDERS AND SHAPES
# ============================================================

BOX_RADIUS: Final[float] = 2 * mm

BOX_BORDER_WIDTH: Final[float] = 0.42
DIVIDER_WIDTH: Final[float] = 0.35

ICON_STROKE: Final[float] = 1.1

OUTER_BORDER_WIDTH: Final[float] = 0.45
INNER_BORDER_WIDTH: Final[float] = BOX_BORDER_WIDTH
ICON_STROKE_WIDTH: Final[float] = ICON_STROKE


# ============================================================
# PADDING
# ============================================================

BOX_PADDING_X: Final[float] = 4 * mm
BOX_PADDING_Y: Final[float] = 3 * mm
TEXT_PADDING: Final[float] = 2 * mm

QUESTION_PADDING_X: Final[float] = 4 * mm
QUESTION_PADDING_Y: Final[float] = 3 * mm

COLUMN_GAP: Final[float] = 2 * mm


# ============================================================
# THEME OBJECT
# ============================================================

@dataclass(frozen=True)
class Theme:
    text: Color = TEXT_BLACK
    heading: Color = HEADING_BLUE
    border: Color = LIGHT_GREY
    divider: Color = LIGHT_GREY
    background: Color = WHITE

    regular_font: str = FONT_REGULAR
    bold_font: str = FONT_BOLD
    italic_font: str = FONT_ITALIC
    bold_italic_font: str = FONT_BOLD_ITALIC


THEME = Theme()