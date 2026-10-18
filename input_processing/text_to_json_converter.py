"""Convert YK Monthly prompt-generated INPUT_DATA.txt to INPUT.json.

Usage (from project root):
    python input_processing/text_to_json_converter.py
    python input_processing/text_to_json_converter.py path/to/INPUT_DATA.txt

Supports the plain-text format in YK Monthly Master Prompt V2.0 and
legacy JSON input. Does not invent source citations or article facts.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUTPUT_PATH = HERE / "INPUT.json"
CANDIDATES = (ROOT / "INPUT_DATA.txt",)


class ConversionError(ValueError):
    pass


LABELS = {
    "ISSUE MONTH", "MAGAZINE", "PUBLICATION DATE", "ISSUE TITLE", "RATING",
    "GS MAPPING", "EDITORIAL SOURCE(S)", "ARTICLE SOURCE TITLE",
    "ARTICLE PAGE REFERENCE", "SOURCE ARTICLE TITLE", "SOURCE PAGE REFERENCE",
    "TODAY'S QUESTION", "QUICK FACTS", "KEY TAKEAWAY", "MAINS QUESTION",
    "MAINS ANSWER", "RECALL ANCHORS", "PRO MAINS QUESTION 1", "PRO MAINS ANSWER 1", "PRO MAINS QUESTION 2", "PRO MAINS ANSWER 2",
}
TOPIC_RE = re.compile(r"TOPIC\s+(\d+)$", re.I)
KP_RE = re.compile(r"KNOWLEDGE POINT\s+([1-5])$", re.I)
MCQ_RE = re.compile(r"(?:DAILY MCQ\s+([1-2])|PRO MCQ\s+([1-5]))$", re.I)
OPTION_RE = re.compile(r"^([A-D])\.\s*(.+)$")
ANSWER_RE = re.compile(r"^Correct Answer:\s*([A-D])\s*$", re.I)
EXPLANATION_RE = re.compile(r"^Explanation:\s*(.*)$", re.I)


def _label(line: str) -> str | None:
    value = line.strip().upper().replace("’", "'")
    if value in LABELS or TOPIC_RE.fullmatch(value) or KP_RE.fullmatch(value) or MCQ_RE.fullmatch(value):
        return value
    return None


def _paragraphs(lines: list[str]) -> list[str]:
    return [" ".join(part.split()) for part in re.split(r"\n\s*\n", "\n".join(lines).strip()) if part.strip()]


def _one(sections: dict[str, list[str]], name: str, where: str, required: bool = True) -> str:
    paragraphs = _paragraphs(sections.get(name, []))
    if not paragraphs:
        if required:
            raise ConversionError(f"{where}: missing {name}")
        return ""
    return " ".join(paragraphs)


def _month(raw: str) -> str:
    raw = raw.strip()
    for fmt in ("%B %Y", "%b %Y", "%Y-%m", "%d.%m.%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(raw, fmt).strftime("%B %Y")
        except ValueError:
            continue
    raise ConversionError(f"Invalid ISSUE MONTH/PUBLICATION DATE: {raw!r}")


def _gs(raw: str) -> list[str]:
    parts = [x.strip() for x in re.split(r"\s*;\s*|\s*\|\s*", raw) if x.strip()]
    result = []
    for part in parts:
        part = re.sub(r"^GS\s+Paper\s+", "GS ", part, flags=re.I)
        result.append(part)
    if not result or not all(re.search(r"\bGS\s+(?:I|II|III|IV)\b", x) for x in result):
        raise ConversionError("GS MAPPING must specify GS I, GS II, GS III or GS IV")
    return result


def _mcq(lines: list[str], where: str) -> dict[str, Any]:
    question_lines: list[str] = []
    options: dict[str, str] = {}
    answer = None
    explanation_lines: list[str] = []
    state = "question"
    for line in lines:
        s = line.strip()
        if not s:
            continue
        match = OPTION_RE.match(s)
        if match:
            state = "options"
            letter = match.group(1)
            if letter in options:
                raise ConversionError(f"{where}: duplicate option {letter}")
            options[letter] = match.group(2)
            continue
        match = ANSWER_RE.match(s)
        if match:
            answer = match.group(1).upper()
            state = "answer"
            continue
        match = EXPLANATION_RE.match(s)
        if match:
            state = "explanation"
            if match.group(1):
                explanation_lines.append(match.group(1))
            continue
        if state == "question":
            question_lines.append(s)
        elif state == "options" and options:
            options[list(options)[-1]] += " " + s
        elif state == "explanation":
            explanation_lines.append(s)
        else:
            raise ConversionError(f"{where}: unexpected text after Correct Answer")
    if list(options) != list("ABCD") or answer not in options or not question_lines or not explanation_lines:
        raise ConversionError(f"{where}: requires question, A-D options, Correct Answer and Explanation")
    return {
        "question": " ".join(question_lines),
        "options": [options[k] for k in "ABCD"],
        "answer": "ABCD".index(answer),
        "explanation": " ".join(explanation_lines),
    }


def _parse_sections(text: str) -> tuple[dict[str, list[str]], list[tuple[int, dict[str, list[str]]]]]:
    common: dict[str, list[str]] = {}
    topics: list[tuple[int, dict[str, list[str]]]] = []
    current = common
    label: str | None = None
    for lineno, line in enumerate(text.replace("\r\n", "\n").replace("\r", "\n").split("\n"), 1):
        heading = _label(line)
        if heading:
            topic_match = TOPIC_RE.fullmatch(heading)
            if topic_match:
                num = int(topic_match.group(1))
                if any(n == num for n, _ in topics):
                    raise ConversionError(f"Line {lineno}: duplicate TOPIC {num}")
                current = {}
                topics.append((num, current))
                label = None
            else:
                if heading in current:
                    raise ConversionError(f"Line {lineno}: duplicate section {heading}")
                current[heading] = []
                label = heading
        elif line.strip():
            if label is None:
                raise ConversionError(f"Line {lineno}: text outside a labelled section: {line[:65]}")
            current[label].append(line.rstrip())
        elif label is not None:
            current[label].append("")
    if not topics:
        raise ConversionError("No TOPIC 1 / TOPIC 2 sections found")
    return common, topics


def _topic(num: int, sections: dict[str, list[str]], magazine: str, issue: str) -> dict[str, Any]:
    where = f"TOPIC {num}"
    knowledge = []
    for i in range(1, 6):
        parts = _paragraphs(sections.get(f"KNOWLEDGE POINT {i}", []))
        if len(parts) != 2:
            raise ConversionError(f"{where}: KNOWLEDGE POINT {i} needs exactly a heading and an explanation, separated by a blank line")
        knowledge.append({"title": parts[0], "text": parts[1]})
    facts = _paragraphs(sections.get("QUICK FACTS", []))
    if len(facts) != 4:
        raise ConversionError(f"{where}: QUICK FACTS requires exactly four separate paragraphs; found {len(facts)}")
    source_title = _one(sections, "ARTICLE SOURCE TITLE", where, False) or _one(sections, "SOURCE ARTICLE TITLE", where, False)
    page = _one(sections, "ARTICLE PAGE REFERENCE", where, False) or _one(sections, "SOURCE PAGE REFERENCE", where, False)
    sources = []
    if source_title:
        source = {"article_title": source_title}
        if page:
            source["page_reference"] = page
        sources.append(source)
    # Do not mistake ISSUE TITLE for the original magazine article title.
    gs = _gs(_one(sections, "GS MAPPING", where))
    result: dict[str, Any] = {
        "id": f"UAK-{'YMA' if magazine == 'Yojana' else 'KMA'}-{datetime.strptime(issue, '%B %Y').strftime('%y%m')}-{num:02d}",
        "series": f"UPSC Anchor with Kumar - {magazine} Study Series",
        "magazine": magazine,
        "issue": issue,
        "topic_number": num,
        "title": _one(sections, "ISSUE TITLE", where),
        "gs_mapping": gs,
        "sources": sources,
        "question": _one(sections, "TODAY'S QUESTION", where),
        "knowledge_points": knowledge,
        "quick_facts": [{"text": f} for f in facts],
        "key_takeaway": _one(sections, "KEY TAKEAWAY", where),
    }
    rating = _one(sections, "RATING", where, False)
    if rating:
        if rating.lower() not in ("high", "medium", "low"):
            raise ConversionError(f"{where}: RATING must be High, Medium or Low")
        # The PDF knowledge loader calls float(rating). Map the editorial
        # selection labels to numeric scores on a 0-100 scale.
        result["rating"] = {"high": 90.0, "medium": 70.0, "low": 50.0}[rating.lower()]
    mains_q = _one(sections, "MAINS QUESTION", where, False)
    mains_lines = sections.get("MAINS ANSWER", [])
    mcq_labels = [x for x in sections if re.fullmatch(r"DAILY MCQ [1-2]", x)]
    if mains_q or mains_lines or mcq_labels:
        if not mains_q:
            raise ConversionError(f"{where}: Pro content requires MAINS QUESTION")
        paragraphs = _paragraphs(mains_lines)
        if len(paragraphs) != 3:
            raise ConversionError(f"{where}: MAINS ANSWER requires exactly three paragraphs")
        if set(mcq_labels) != {"DAILY MCQ 1", "DAILY MCQ 2"}:
            raise ConversionError(f"{where}: Pro content requires exactly DAILY MCQ 1 and DAILY MCQ 2")
        # PDF schema uses an array of body arguments. A single body paragraph
        # is preserved as one argument; no content is invented or rewritten.
        result["mains"] = {
            "question": mains_q,
            "answer": {
                "introduction": paragraphs[0],
                "body": [{"heading": "", "text": paragraphs[1]}],
                "conclusion": paragraphs[2],
            },
        }
        result["mcqs"] = [_mcq(sections[f"DAILY MCQ {i}"], f"{where} MCQ {i}") for i in (1, 2)]
    # Pro-only fields do not change the Normal edition's 2-MCQ schema.
    pro_labels = [f"PRO MAINS QUESTION {i}" for i in (1, 2)] + [f"PRO MAINS ANSWER {i}" for i in (1, 2)] + [f"PRO MCQ {i}" for i in range(1, 6)]
    present = [label for label in pro_labels if label in sections]
    if present:
        missing = [label for label in pro_labels if label not in sections]
        if missing:
            raise ConversionError(f"{where}: incomplete new Pro content; missing {', '.join(missing)}")
        pro_answers = []
        for i in (1, 2):
            q = _one(sections, f"PRO MAINS QUESTION {i}", where)
            paragraphs = _paragraphs(sections[f"PRO MAINS ANSWER {i}"])
            if len(paragraphs) != 3:
                raise ConversionError(f"{where}: PRO MAINS ANSWER {i} requires 3 paragraphs (intro, body, conclusion)")
            pro_answers.append({"question": q, "answer": {"paragraphs": paragraphs}})
        result["pro_mains_answers"] = pro_answers
        result["pro_mcqs"] = [_mcq(sections[f"PRO MCQ {i}"], f"{where} PRO MCQ {i}") for i in range(1, 6)]
    result["validation"] = {"source_policy": "Article grounding not checked by converter", "approval": "pending_article_audit"}
    return result


def convert_text(text: str) -> dict[str, Any]:
    if text.lstrip().startswith("{"):
        data = json.loads(text)
        if not isinstance(data, dict):
            raise ConversionError("JSON root must be an object")
        return data
    common, topics = _parse_sections(text)
    magazine = _one(common, "MAGAZINE", "Issue").capitalize()
    if magazine not in ("Yojana", "Kurukshetra"):
        raise ConversionError("MAGAZINE must be Yojana or Kurukshetra")
    issue_raw = _one(common, "ISSUE MONTH", "Issue", False) or _one(common, "PUBLICATION DATE", "Issue")
    issue = _month(issue_raw)
    # The publication module requires publication_date on the top-level object.
    # Monthly issues do not specify a release day, so use the first day of the
    # issue month as a stable technical date, not a claimed release date.
    month_date = datetime.strptime(issue, "%B %Y")
    result = {
        "schema_version": "2.0",
        "publication_date": month_date.strftime("%d %B %Y"),
        "publication_date_iso": month_date.strftime("%Y-%m-%d"),
        "topic_count": len(topics),
        "magazine": magazine,
        "issue": issue,
        "topics": [_topic(n, s, magazine, issue) for n, s in topics],
    }
    # Keep the publication wrapper for one-topic and multi-topic runs alike.
    return result


def convert_file(source_path: Path, output_path: Path = OUTPUT_PATH) -> Path:
    try:
        text = source_path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise ConversionError(f"Cannot read {source_path}: {exc}") from exc
    data = convert_text(text)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output_path


def main() -> int:
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else next((p for p in CANDIDATES if p.is_file()), None)
    if source is None:
        print("No INPUT_DATA.txt found in the project root")
        return 1
    try:
        output = convert_file(source)
    except (ConversionError, ValueError) as exc:
        print(f"Conversion FAILED: {exc}")
        return 1
    print(f"Converted {source} -> {output}")
    print("NOTE: Source-grounding and project validator checks must be run separately.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
