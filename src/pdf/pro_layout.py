"""New Pro-only layout. Does not modify the Normal edition layout."""
from dataclasses import dataclass
from reportlab.lib.units import mm
from src.pdf.page_setup import Rect
from src.config import CONTENT_HEIGHT, CONTENT_WIDTH, PAGE_MARGIN_BOTTOM, PAGE_MARGIN_LEFT

HEADER_HEIGHT = 12 * mm
FOOTER_HEIGHT = 6 * mm
GAP = 1.2 * mm
LEFT_RATIO = 0.50  # Left mains column; right MCQ column

@dataclass(frozen=True)
class ProLayout:
    header: Rect
    footer: Rect
    topic_bar: Rect
    mains_1: Rect
    mains_2: Rect
    mcqs: Rect

def get_pro_layout():
    page = Rect(PAGE_MARGIN_LEFT, PAGE_MARGIN_BOTTOM, CONTENT_WIDTH, CONTENT_HEIGHT)
    header = Rect(page.x, page.top-HEADER_HEIGHT, page.width, HEADER_HEIGHT)
    footer = Rect(page.x, page.y, page.width, FOOTER_HEIGHT)
    body_top = header.y-GAP
    body_bottom = footer.top+GAP
    topic_height = 12*mm  # Topic heading + GS mapping, fixed height
    topic_bar = Rect(page.x, body_top-topic_height, page.width, topic_height)
    content_top = topic_bar.y-GAP
    content = Rect(page.x, body_bottom, page.width, content_top-body_bottom)
    left, right = content.split_vertical(LEFT_RATIO, GAP)
    top, bottom = left.split_horizontal(3 / 8, GAP)
    return ProLayout(header, footer, topic_bar, top, bottom, right)
