"""Pro Edition: two Mains answers on the left; five MCQs on the right.

Requires explicit pro_mains_answers and pro_mcqs in INPUT.json.
No invented or duplicated educational content; Normal PDF is unaffected.
"""
from __future__ import annotations
import json
from pathlib import Path
from dataclasses import replace
from xml.sax.saxutils import escape
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_CENTER
from src.components.header import HeaderData, draw_header
from src.components.footer import FooterData, draw_footer
from src.pdf.page_setup import begin_page, create_canvas, finish_page
from src.pdf.pro_layout import get_pro_layout
from src.pdf.helpers import paragraph_style
from src.pdf.theme import (FONT_REGULAR, FONT_BOLD, HEADING_BLUE, BLACK,
                           SECTION_TITLE_SIZE, MAINS_TEXT_SIZE, MAINS_QUESTION_SIZE,
                           MCQ_QUESTION_SIZE, MCQ_OPTION_SIZE)
from src.publication import PublicationMetadata, build_publication_metadata
from src.knowledge_engine.knowledge_loader import INPUT_JSON

# Pro-only heading sizes (points).
PRO_SECTION_HEADING_SIZE = 12
PRO_TOPIC_HEADING_SIZE = 13.5


def _p(text, font, size, width, bold=False, first_line_indent=0):
    style = paragraph_style('NewPro'+str(size)+('b' if bold else ''),
        font_name=font, font_size=size, leading=size+2, text_color=BLACK)
    style.firstLineIndent = first_line_indent
    para = Paragraph(escape(str(text)), style)
    _, h = para.wrap(width, 99999)
    return para, h


def _render_items(canvas, rect, title, items, min_size, max_shrink=0.5):
    """Render measured paragraphs; reject overflows instead of clipping text."""
    pad = 3*mm
    width = rect.width-2*pad
    top = rect.top-pad
    bottom = rect.y+pad
    for step in range(6):
        shrink = step*0.1
        measures=[]
        total=0
        for text, font, base_size, gap in items:
            indent = 3*mm if title.startswith("MAINS ") and font == FONT_REGULAR else 0
            para, height = _p(text, font, base_size-shrink, width, first_line_indent=indent)
            measures.append((para,height,gap))
            total+=height+gap
        if total <= top-bottom-PRO_SECTION_HEADING_SIZE-5*mm:
            break
    else:
        raise ValueError(f'{title}: content exceeds panel (max font shrink {max_shrink} pt). Shorten content or enlarge the panel.')
    canvas.saveState()
    canvas.setStrokeColorRGB(.72,.77,.84)
    canvas.setLineWidth(.55)
    canvas.roundRect(rect.x,rect.y,rect.width,rect.height,2*mm,stroke=1,fill=0)
    canvas.setFillColor(HEADING_BLUE)
    canvas.setFont(FONT_BOLD, PRO_SECTION_HEADING_SIZE)
    canvas.drawCentredString(rect.centre_x, top-PRO_SECTION_HEADING_SIZE, title)
    y=top-PRO_SECTION_HEADING_SIZE-5*mm
    for para,height,gap in measures:
        y-=height
        para.drawOn(canvas,rect.x+pad,y)
        y-=gap
    canvas.restoreState()


def _answer_items(raw):
    q = raw['question']
    parts = raw['answer']['paragraphs']
    return [(q,FONT_BOLD,MAINS_QUESTION_SIZE,2*mm)] + [
        (p,FONT_REGULAR,MAINS_TEXT_SIZE,1.5*mm if i<2 else 0)
        for i,p in enumerate(parts)]


def _mcq_items(mcqs):
    items=[]
    for i,m in enumerate(mcqs,1):
        items.append((f'{i}. {m["question"]}',FONT_BOLD,MCQ_QUESTION_SIZE,1.3*mm))
        options=m['options']
        if isinstance(options,dict):
            options=[options[k] for k in 'ABCD']
        for letter,option in zip('ABCD',options):
            items.append((f'{letter}. {option}',FONT_REGULAR,MCQ_OPTION_SIZE,.45*mm))
        a=m.get('answer',m.get('correct_answer'))
        a='ABCD'[a] if type(a) is int else str(a)
        items.append((f'Correct Answer: {a}',FONT_BOLD,MCQ_OPTION_SIZE,.8*mm))
        items.append((f'Explanation: {m["explanation"]}',FONT_REGULAR,MCQ_OPTION_SIZE,3.0*mm if i<5 else 0))
    return items


def _read_pro_topics():
    data=json.loads(Path(INPUT_JSON).read_text(encoding='utf-8-sig'))
    topics=data['topics'] if 'topics' in data else [data]
    for i,topic in enumerate(topics,1):
        answers=topic.get('pro_mains_answers')
        mcqs=topic.get('pro_mcqs')
        if not isinstance(answers,list) or len(answers)!=2 or not isinstance(mcqs,list) or len(mcqs)!=5:
            raise ValueError(f'Topic {i}: Pro PDF requires 2 PRO MAINS QUESTION/ANSWER sections and 5 PRO MCQs in INPUT_DATA.txt. Existing Normal sections remain unchanged.')
    return topics


def generate_pro_pdf(output_path: Path, metadata: PublicationMetadata | None = None) -> Path:
    topics=_read_pro_topics()
    meta=metadata if metadata is not None else build_publication_metadata()
    # Convert metadata to the Pro identity, even when supplied by the main runner.
    if not meta.title.endswith(' - PRO'):
        meta = replace(meta, title=meta.title + ' - PRO')
    if '-PRO-' not in meta.edition_code:
        code_parts = meta.edition_code.rsplit('-', 1)
        if len(code_parts) == 2:
            meta = replace(meta, edition_code=code_parts[0] + '-PRO-' + code_parts[1])
    output_path=Path(output_path)
    output_path.parent.mkdir(parents=True,exist_ok=True)
    canvas=create_canvas(str(output_path))
    layout=get_pro_layout()
    for i,topic in enumerate(topics,1):
        begin_page(canvas)
        draw_header(canvas=canvas,rect=layout.header,data=HeaderData(
            title=meta.title,subtitle=meta.subtitle,publication_date=meta.publication_date,
            edition_code=meta.edition_code),compact=False)
        canvas.saveState()
        canvas.setStrokeColorRGB(.72,.77,.84)
        canvas.roundRect(layout.topic_bar.x,layout.topic_bar.y,layout.topic_bar.width,
                         layout.topic_bar.height,2*mm,stroke=1,fill=0)
        title=topic.get('title',topic.get('issue_title','Topic'))
        gs=topic.get('gs_mapping','')
        gs=gs[0] if isinstance(gs,list) and gs else gs
        gs=gs.get('paper','') if isinstance(gs,dict) else gs
        _render_topic_title(canvas,layout.topic_bar,title,str(gs))
        canvas.restoreState()
        _render_items(canvas,layout.mains_1,'MAINS QUESTION 1',_answer_items(topic['pro_mains_answers'][0]),MAINS_TEXT_SIZE)
        _render_items(canvas,layout.mains_2,'MAINS QUESTION 2',_answer_items(topic['pro_mains_answers'][1]),MAINS_TEXT_SIZE)
        _render_items(canvas,layout.mcqs,'PRACTICE MCQs (5)',_mcq_items(topic['pro_mcqs']),MCQ_OPTION_SIZE)
        draw_footer(canvas=canvas,rect=layout.footer,data=FooterData(
            brand_name=meta.footer_brand,publication_code=meta.edition_code,
            page_number=i,total_pages=len(topics)))
        finish_page(canvas)
    canvas.save()
    return output_path


def _render_topic_title(canvas,rect,title,gs):
    gs_label = gs.split(' - ',1)[0] if gs else ''
    gs_width = rect.width * 0.10
    width = rect.width * 0.90 - 6*mm
    # Center the text itself within the left 90% (not merely the paragraph box).
    style = paragraph_style('ProTopicCentered', font_name=FONT_BOLD,
                            font_size=PRO_TOPIC_HEADING_SIZE,
                            leading=PRO_TOPIC_HEADING_SIZE+2, text_color=BLACK)
    style.alignment = TA_CENTER
    style.leftIndent = 0
    style.rightIndent = 0
    style.firstLineIndent = 0
    style.spaceBefore = 0
    style.spaceAfter = 0
    p = Paragraph(escape(str(title)), style)
    _, h = p.wrap(width, 99999)
    if h > rect.height-3*mm:
        raise ValueError('Topic title too long for topic bar')
    p.drawOn(canvas,rect.x+3*mm,rect.centre_y-h/2)
    if gs_label:
        canvas.setStrokeColorRGB(.72,.77,.84)
        canvas.line(rect.right-gs_width,rect.y,rect.right-gs_width,rect.top)
        canvas.setFillColor(HEADING_BLUE)
        canvas.setFont(FONT_BOLD,9)
        canvas.drawRightString(rect.right-3*mm,rect.centre_y-3,gs_label)


def generate_pro_pdf_preview(output_path: Path,metadata: PublicationMetadata | None=None)->Path:
    return generate_pro_pdf(output_path,metadata)
