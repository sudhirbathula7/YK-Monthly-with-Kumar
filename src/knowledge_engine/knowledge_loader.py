"""Load monthly magazine topics while preserving the original PDF generator API.

Loads five Quick Facts without obsolete content models.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_JSON = PROJECT_ROOT / 'input_processing' / 'INPUT.json'

class KnowledgeLoadError(ValueError):
    pass

@dataclass(frozen=True)
class GSMapping:
    paper: str
    subject: str = ''
    syllabus: str = ''

@dataclass(frozen=True)
class KnowledgePointRecord:
    heading: str
    explanation: str

@dataclass(frozen=True)
class MCQRecord:
    question: str
    options: tuple[str, str, str, str]
    correct_answer: str
    explanation: str

@dataclass(frozen=True)
class TopicRecord:
    topic_number: int
    issue_title: str
    rating: float
    editorial_sources: tuple[str, ...]
    gs_mapping: GSMapping
    todays_question: str
    recall_anchors: tuple[str, ...]
    knowledge_points: tuple[KnowledgePointRecord, ...]
    key_takeaway: str
    mains_question: str
    mains_answer: str
    daily_mcqs: tuple[MCQRecord, ...]
    quick_facts: tuple[str, ...]

    @property
    def mcqs(self) -> tuple[MCQRecord, ...]:
        return self.daily_mcqs


def _required(obj: dict[str, Any], key: str, where: str) -> Any:
    if key not in obj:
        raise KnowledgeLoadError(f'{where}: missing {key}')
    return obj[key]


def _list(value: Any, where: str, minimum: int, maximum: int) -> list[Any]:
    if not isinstance(value, (list, tuple)) or not minimum <= len(value) <= maximum:
        raise KnowledgeLoadError(f'{where}: expected {minimum} to {maximum} items')
    return list(value)


def _string(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise KnowledgeLoadError(f'{where}: nonempty text required')
    return value.strip()


def _gs_paper(value: Any, where: str) -> GSMapping:
    """Accept GS II, GS Paper II, and the magazine's GS mapping list."""
    if isinstance(value, list):
        value = _list(value, where, 1, 4)[0]
    if isinstance(value, dict):
        raw = _string(value.get('paper', value.get('display')), where)
        subject = str(value.get('subject') or '')
        syllabus = str(value.get('syllabus') or '')
    else:
        raw = _string(value, where)
        subject = syllabus = ''
    match = re.match(r'^GS\s*(?:Paper\s*)?(IV|III|II|I|[1-4])(?=\b|\s|\W|$)', raw, re.I)
    if not match:
        raise KnowledgeLoadError(f'{where}: expected GS I, GS II, GS III or GS IV')
    roman = {'1': 'I', '2': 'II', '3': 'III', '4': 'IV'}
    paper = roman.get(match.group(1).upper(), match.group(1).upper())
    return GSMapping('GS ' + paper, subject, syllabus)


def _text_field(obj: dict[str, Any], names: tuple[str, ...], where: str) -> str:
    for name in names:
        if name in obj and obj[name] is not None:
            return _string(obj[name], where)
    raise KnowledgeLoadError(f'{where}: missing {" or ".join(names)}')


def _mains_answer(raw: Any, where: str) -> str:
    if isinstance(raw, str):
        return _string(raw, where)
    if not isinstance(raw, dict):
        raise KnowledgeLoadError(f'{where}: expected text or structured answer')
    if raw.get('full_text'):
        return _string(raw['full_text'], where)
    if isinstance(raw.get('paragraphs'), list):
        return _string('\n\n'.join(_string(p, where) for p in raw['paragraphs']), where)
    paragraphs = []
    for key in ('introduction', 'body', 'conclusion'):
        part = raw.get(key)
        if isinstance(part, list):
            paragraphs.extend(_text_field(p, ('text',), where) if isinstance(p, dict) else _string(p, where) for p in part)
        elif isinstance(part, str) and part.strip():
            paragraphs.append(part.strip())
    return _string('\n\n'.join(paragraphs), where)


def _load_topic(raw: dict[str, Any], position: int) -> TopicRecord:
    where = f'Topic {position}'
    if not isinstance(raw, dict):
        raise KnowledgeLoadError(f'{where}: expected object')
    gs = _gs_paper(_required(raw, 'gs_mapping', where), f'{where}.gs_mapping')

    points = []
    for i, p in enumerate(_list(_required(raw, 'knowledge_points', where), f'{where}.knowledge_points', 5, 5), 1):
        if not isinstance(p, dict):
            raise KnowledgeLoadError(f'{where}.knowledge_points[{i}]: expected object')
        points.append(KnowledgePointRecord(
            _text_field(p, ('heading', 'title'), f'{where}.point{i}.heading'),
            _text_field(p, ('explanation', 'text'), f'{where}.point{i}.explanation')))

    # Quick Facts are mandatory: never manufacture them from other sections.
    facts_raw = _list(_required(raw, 'quick_facts', where), f'{where}.quick_facts', 4, 4)
    facts = tuple(_string(f.get('text') if isinstance(f, dict) else f, f'{where}.quick_facts') for f in facts_raw)

    mcqs_raw = _list(raw.get('mcqs', raw.get('daily_mcqs')), f'{where}.mcqs', 2, 2)
    mcqs = []
    for i, m in enumerate(mcqs_raw, 1):
        if not isinstance(m, dict):
            raise KnowledgeLoadError(f'{where}.mcq{i}: expected object')
        opts = m.get('options')
        if isinstance(opts, dict):
            opts = [opts.get(k) for k in 'ABCD']
        options = tuple(_string(o, f'{where}.mcq{i}.options') for o in _list(opts, f'{where}.mcq{i}.options', 4, 4))
        answer_raw = m.get('correct_answer', m.get('answer'))
        if isinstance(answer_raw, int) and not isinstance(answer_raw, bool):
            if not 0 <= answer_raw <= 3:
                raise KnowledgeLoadError(f'{where}.mcq{i}: answer index must be 0–3')
            answer = 'ABCD'[answer_raw]
        else:
            answer = _string(answer_raw, f'{where}.mcq{i}.answer').upper()
        if answer not in ('A', 'B', 'C', 'D'):
            raise KnowledgeLoadError(f'{where}.mcq{i}: answer must be A/B/C/D or index 0–3')
        mcqs.append(MCQRecord(_string(m.get('question'), f'{where}.mcq{i}.question'), options, answer,
                              _string(m.get('explanation'), f'{where}.mcq{i}.explanation')))

    mains = raw.get('mains')
    if isinstance(mains, dict):
        mains_question = _text_field(mains, ('question',), f'{where}.mains.question')
        mains_answer = _mains_answer(mains.get('answer'), f'{where}.mains.answer')
    else:
        mains_question = _string(_required(raw, 'mains_question', where), f'{where}.mains_question')
        mains_answer = _mains_answer(_required(raw, 'mains_answer', where), f'{where}.mains_answer')

    sources_raw = raw.get('sources', raw.get('editorial_sources'))
    sources = _list(sources_raw, f'{where}.sources', 1, 20)
    source_names = []
    for i, source in enumerate(sources, 1):
        if isinstance(source, dict):
            source_names.append(_text_field(source, ('article_title', 'article', 'title'), f'{where}.source{i}'))
        else:
            source_names.append(_string(source, f'{where}.source{i}'))
    anchors = raw.get('recall_anchors')
    if anchors is None or anchors == []:
        anchors = [p.heading for p in points]
    else:
        anchors = [_string(a, f'{where}.recall_anchors') for a in _list(anchors, f'{where}.recall_anchors', 5, 5)]

    number = raw.get('topic_number', position)
    try:
        number = int(number)
        rating = float(raw.get('rating', 0))
    except (TypeError, ValueError) as exc:
        raise KnowledgeLoadError(f'{where}: invalid topic_number or rating') from exc
    return TopicRecord(
        topic_number=number,
        issue_title=_text_field(raw, ('issue_title', 'topic_title', 'title'), f'{where}.issue_title'),
        rating=rating, editorial_sources=tuple(source_names), gs_mapping=gs,
        todays_question=_text_field(raw, ('todays_question', 'question'), f'{where}.todays_question'),
        recall_anchors=tuple(anchors), knowledge_points=tuple(points),
        key_takeaway=_string(_required(raw, 'key_takeaway', where), f'{where}.key_takeaway'),
        mains_question=mains_question, mains_answer=mains_answer,
        daily_mcqs=tuple(mcqs), quick_facts=facts)


def load_topics(input_path: Path = INPUT_JSON) -> tuple[TopicRecord, ...]:
    try:
        data = json.loads(Path(input_path).read_text(encoding='utf-8-sig'))
    except (OSError, json.JSONDecodeError) as exc:
        raise KnowledgeLoadError(f'Cannot read valid input JSON: {exc}') from exc
    if isinstance(data, dict) and 'topics' in data:
        topics = data['topics']
    elif isinstance(data, dict):
        topics = [data]  # one-topic pilot file
    else:
        topics = None
    if not isinstance(topics, list) or not topics:
        raise KnowledgeLoadError('INPUT.json requires a nonempty topics list')
    return tuple(_load_topic(raw, i) for i, raw in enumerate(topics, 1))
