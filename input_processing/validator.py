"""Validate YK Monthly content for Normal and Pro editions.

Checks format and word limits; article-level factual verification remains editorial.
Accepts a single-topic pilot or a monthly ``topics`` collection.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_JSON_PATH = PROJECT_ROOT / 'input_processing' / 'INPUT.json'
WORD_RE = re.compile(r"\b[\w]+(?:[’'-][\w]+)*\b", re.UNICODE)


def _words(value: str) -> int:
    return len(WORD_RE.findall(value))


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _fact_text(value: Any) -> str | None:
    if isinstance(value, dict):
        value = value.get('text')
    return value.strip() if _text(value) else None


def _answer_parts(topic: dict) -> tuple[str, str, str] | None:
    mains = topic.get('mains')
    answer = mains.get('answer') if isinstance(mains, dict) else topic.get('mains_answer')
    if isinstance(answer, dict):
        paragraphs = answer.get('paragraphs')
        if isinstance(paragraphs, list) and len(paragraphs) == 3 and all(_text(p) for p in paragraphs):
            return tuple(paragraphs)  # type: ignore[return-value]
        intro, body, conclusion = answer.get('introduction'), answer.get('body'), answer.get('conclusion')
        if _text(intro) and _text(conclusion):
            if isinstance(body, list) and body and all(isinstance(p, dict) and _text(p.get('text')) for p in body):
                return intro, ' '.join(p['text'] for p in body), conclusion
            if _text(body):
                return intro, body, conclusion
    return None


def validate_data(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ['Root must be a JSON object']
    magazine = data.get('magazine')
    if magazine is not None and magazine not in ('Yojana', 'Kurukshetra'):
        errors.append('magazine must be Yojana or Kurukshetra')
    month = data.get('issue_month')
    if month is not None and (not isinstance(month, str) or not re.fullmatch(r'\d{4}-(0[1-9]|1[0-2])', month)):
        errors.append('issue_month must be YYYY-MM')
    if 'topics' in data:
        topics = data['topics']
        if not isinstance(topics, list) or not topics:
            return errors + ['topics must be a nonempty list']
        if 'topic_count' in data and data['topic_count'] != len(topics):
            errors.append('topic_count must equal the number of topics')
    else:
        topics = [data]
    seen: set[int] = set()
    for idx, topic in enumerate(topics, 1):
        p = f'Topic {idx}'
        if not isinstance(topic, dict):
            errors.append(f'{p}: must be an object')
            continue
        number = topic.get('topic_number', idx)
        if type(number) is not int or number < 1 or number in seen:
            errors.append(f'{p}: topic_number must be a unique positive integer')
        else:
            seen.add(number)
        if not any(_text(topic.get(k)) for k in ('issue_title', 'topic_title', 'title')):
            errors.append(f'{p}: title required')
        if not any(_text(topic.get(k)) for k in ('todays_question', 'question')):
            errors.append(f'{p}: question required')
        gs = topic.get('gs_mapping')
        valid_gs = lambda s: _text(s) and bool(re.match(r'^GS\s*(?:I|II|III|IV|[1-4])\b', s, re.I))
        if not (valid_gs(gs) or (isinstance(gs, list) and gs and all(valid_gs(s) for s in gs)) or (isinstance(gs, dict) and valid_gs(gs.get('paper')))):
            errors.append(f'{p}: invalid gs_mapping')
        sources = topic.get('sources', topic.get('editorial_sources'))
        if not isinstance(sources, list) or not sources:
            errors.append(f'{p}: at least one internal source reference required')
        else:
            for j, source in enumerate(sources, 1):
                if isinstance(source, dict):
                    if not any(_text(source.get(k)) for k in ('article_title', 'article', 'title')):
                        errors.append(f'{p}: source {j} needs an article title')
                elif not _text(source):
                    errors.append(f'{p}: source {j} must be nonempty')
        points = topic.get('knowledge_points')
        if not isinstance(points, list) or len(points) != 5:
            errors.append(f'{p}: knowledge_points requires exactly 5 items')
        else:
            for j, point in enumerate(points, 1):
                if not isinstance(point, dict) or not any(_text(point.get(k)) for k in ('heading', 'title')) or not any(_text(point.get(k)) for k in ('explanation', 'text')):
                    errors.append(f'{p}: knowledge point {j} requires a heading and explanation')
                    continue
                heading = point.get('heading', point.get('title', ''))
                explanation = point.get('explanation', point.get('text', ''))
                count = _words(heading) + _words(explanation)
                if count > 35:
                    errors.append(f'{p}: knowledge point {j} has {count} words; maximum 35 including heading')
        facts = topic.get('quick_facts')
        if not isinstance(facts, list) or len(facts) != 4:
            errors.append(f'{p}: quick_facts requires exactly 4 items')
        else:
            total_fact_words = 0
            for j, fact in enumerate(facts, 1):
                value = _fact_text(fact)
                if value is None:
                    errors.append(f'{p}: Quick Fact {j} needs text')
                    continue
                count = _words(value)
                total_fact_words += count
                if not 22 <= count <= 27:
                    errors.append(f'{p}: Quick Fact {j} has {count} words; required 22–27')
            if total_fact_words > 110:
                errors.append(f'{p}: Quick Facts total is {total_fact_words} words; maximum 110')
            total_facts = sum(_words(_fact_text(f) or '') for f in facts)
            if total_facts > 110:
                errors.append(f'{p}: Quick Facts total {total_facts} words; maximum 110')
        takeaway = topic.get('key_takeaway')
        if not _text(takeaway):
            errors.append(f'{p}: key_takeaway required')
        elif _words(takeaway) > 30:
            errors.append(f'{p}: key_takeaway has {_words(takeaway)} words; maximum 30')
        mains = topic.get('mains')
        question = mains.get('question') if isinstance(mains, dict) else topic.get('mains_question')
        if not _text(question):
            errors.append(f'{p}: Mains question required')
        parts = _answer_parts(topic)
        if parts is None:
            errors.append(f'{p}: Mains answer requires introduction, body and conclusion')
        else:
            counts = tuple(_words(part) for part in parts)
            if any(actual > limit for actual, limit in zip(counts, (30, 140, 30))):
                errors.append(f'{p}: Mains word counts are {counts}; maximum (30, 140, 30), excluding body headings')
        # Pro-only validation. The Normal edition still uses exactly 2 daily MCQs.
        pro_answers = topic.get('pro_mains_answers')
        pro_mcqs = topic.get('pro_mcqs')
        if (pro_answers is None) != (pro_mcqs is None):
            errors.append(f'{p}: new Pro content requires both pro_mains_answers and pro_mcqs')
        if pro_answers is not None:
            if not isinstance(pro_answers, list) or len(pro_answers) != 2:
                errors.append(f'{p}: pro_mains_answers requires exactly 2 items')
            else:
                for j, item in enumerate(pro_answers, 1):
                    if not isinstance(item, dict) or not _text(item.get('question')):
                        errors.append(f'{p}: Pro Mains {j} needs a question')
                        continue
                    answer = item.get('answer')
                    parts = answer.get('paragraphs') if isinstance(answer, dict) else None
                    if not isinstance(parts, list) or len(parts) != 3 or not all(_text(x) for x in parts):
                        errors.append(f'{p}: Pro Mains {j} needs 3 nonempty answer paragraphs')
        if pro_mcqs is not None:
            if not isinstance(pro_mcqs, list) or len(pro_mcqs) != 5:
                errors.append(f'{p}: pro_mcqs requires exactly 5 items')
            else:
                for j, m in enumerate(pro_mcqs, 1):
                    if not isinstance(m, dict) or not _text(m.get('question')) or not _text(m.get('explanation')):
                        errors.append(f'{p}: Pro MCQ {j} needs a question and explanation')
                        continue
                    opts = m.get('options')
                    if isinstance(opts, dict):
                        opts = [opts.get(k) for k in 'ABCD']
                    if not isinstance(opts, list) or len(opts) != 4 or not all(_text(x) for x in opts):
                        errors.append(f'{p}: Pro MCQ {j} needs 4 options')
                    a = m.get('answer', m.get('correct_answer'))
                    if type(a) is bool or a not in (0, 1, 2, 3, 'A', 'B', 'C', 'D'):
                        errors.append(f'{p}: Pro MCQ {j} needs a valid correct answer')
        mcqs = topic.get('mcqs', topic.get('daily_mcqs'))
        if not isinstance(mcqs, list) or len(mcqs) != 2:
            errors.append(f'{p}: mcqs requires exactly 2 items')
        else:
            for j, mcq in enumerate(mcqs, 1):
                if not isinstance(mcq, dict):
                    errors.append(f'{p}: MCQ {j} must be an object')
                    continue
                if not _text(mcq.get('question')) or not _text(mcq.get('explanation')):
                    errors.append(f'{p}: MCQ {j} requires question and explanation')
                options = mcq.get('options')
                if isinstance(options, dict):
                    options = [options.get(k) for k in 'ABCD']
                if not isinstance(options, list) or len(options) != 4 or not all(_text(o) for o in options):
                    errors.append(f'{p}: MCQ {j} requires four options')
                answer = mcq.get('correct_answer', mcq.get('answer'))
                if answer not in ('A', 'B', 'C', 'D', 0, 1, 2, 3) or type(answer) is bool:
                    errors.append(f'{p}: MCQ {j} answer must be A/B/C/D or index 0–3')
                if _text(mcq.get('explanation')) and _words(mcq['explanation']) > 60:
                    errors.append(f'{p}: MCQ {j} explanation exceeds maximum 60 words')
    return errors


def validate_file(path: Path = INPUT_JSON_PATH) -> bool:
    try:
        data = json.loads(Path(path).read_text(encoding='utf-8-sig'))
    except (OSError, ValueError) as exc:
        print(f'INPUT.json validation FAILED: {exc}')
        return False
    errors = validate_data(data)
    if errors:
        print(f'INPUT.json validation FAILED ({len(errors)} errors):')
        for error in errors:
            print(f' - {error}')
        return False
    count = len(data['topics']) if 'topics' in data else 1
    print(f'INPUT.json structural validation PASSED: {count} topic(s)')
    print('Article-grounding and content-overlap audits must be completed separately.')
    return True


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else INPUT_JSON_PATH
    return 0 if validate_file(path) else 1


if __name__ == '__main__':
    raise SystemExit(main())
