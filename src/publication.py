from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Final

from src.config import (
    PROJECT_NAME,
    PROJECT_VERSION,
    PUBLICATION_SUBTITLE,
    PUBLICATION_TITLE,
)


# ============================================================
# PUBLICATION IDENTITY
# ============================================================

TELEGRAM_HANDLE: Final[str] = "@upscissueswithkumar"

# Keep empty until the final website/domain is confirmed.
WEBSITE: Final[str] = ""

EDITION_PREFIX: Final[str] = "UAK"

STANDARD_PDF_FILENAME: Final[str] = (
    "UPSC_Anchor_with_Kumar.pdf"
)

PRO_PDF_FILENAME: Final[str] = (
    "UPSC_Anchor_with_Kumar_Pro.pdf"
)


# ============================================================
# INPUT PATH
# ============================================================

PROJECT_ROOT: Final[Path] = (
    Path(__file__).resolve().parent.parent
)

INPUT_JSON_PATH: Final[Path] = (
    PROJECT_ROOT
    / "input_processing"
    / "INPUT.json"
)

PUBLICATION_DATE_FORMAT: Final[str] = (
    "%d %B %Y"  # Accepted input format; PDF display uses Month YYYY.
)


# ============================================================
# PUBLICATION METADATA
# ============================================================

@dataclass(frozen=True, slots=True)
class PublicationMetadata:
    project_name: str
    project_version: str

    title: str
    subtitle: str
    footer_brand: str

    publication_date: str
    publication_date_iso: str
    edition_code: str

    telegram_handle: str
    website: str


# ============================================================
# INPUT METADATA LOADER
# ============================================================

def _load_input_metadata() -> tuple[str, str, str]:
    """
    Load the publication date from validated INPUT.json.

    Returns:
        publication_date:
            Example: 30 July 2026

        publication_date_iso:
            Example: 2026-07-30
    """

    try:
        data = json.loads(
            INPUT_JSON_PATH.read_text(
                encoding="utf-8-sig"
            )
        )

    except FileNotFoundError as exc:
        raise FileNotFoundError(
            "INPUT.json was not found. Run the text-to-JSON "
            f"converter first:\n{INPUT_JSON_PATH}"
        ) from exc

    except json.JSONDecodeError as exc:
        raise ValueError(
            "INPUT.json contains invalid JSON at "
            f"line {exc.lineno}, column {exc.colno}: "
            f"{exc.msg}"
        ) from exc

    except OSError as exc:
        raise OSError(
            f"Unable to read INPUT.json: {exc}"
        ) from exc

    if not isinstance(data, dict):
        raise ValueError(
            "INPUT.json root must be a JSON object."
        )

    magazine = str(data.get("magazine", "")).strip()
    topics = data.get("topics", [])
    if not magazine and isinstance(topics, list):
        names = {str(t.get("magazine", "")).strip().casefold() for t in topics
                 if isinstance(t, dict) and str(t.get("magazine", "")).strip()}
        if len(names) > 1:
            raise ValueError("INPUT.json mixes Yojana and Kurukshetra topics.")
        if names:
            magazine = next(iter(names))
    magazine = magazine.casefold()
    if magazine not in ("yojana", "kurukshetra"):
        raise ValueError("INPUT.json needs magazine: Yojana or Kurukshetra (root or topic).")

    publication_date = str(
        data.get("publication_date", "")
    ).strip()

    publication_date_iso = str(
        data.get("publication_date_iso", "")
    ).strip()

    if not publication_date:
        raise ValueError(
            "INPUT.json is missing 'publication_date'."
        )

    if not publication_date_iso:
        raise ValueError(
            "INPUT.json is missing 'publication_date_iso'."
        )

    try:
        parsed_display_date = datetime.strptime(
            publication_date,
            PUBLICATION_DATE_FORMAT,
        )

    except ValueError as exc:
        raise ValueError(
            "INPUT.json publication_date must use the "
            "format 'DD Month YYYY', for example "
            "'30 July 2026'."
        ) from exc

    try:
        parsed_iso_date = datetime.strptime(
            publication_date_iso,
            "%Y-%m-%d",
        )

    except ValueError as exc:
        raise ValueError(
            "INPUT.json publication_date_iso must use "
            "the format 'YYYY-MM-DD'."
        ) from exc

    if (
        parsed_display_date.date()
        != parsed_iso_date.date()
    ):
        raise ValueError(
            "publication_date and publication_date_iso "
            "represent different dates."
        )

    normalized_display_date = (
        parsed_display_date.strftime(
            PUBLICATION_DATE_FORMAT
        )
    )

    normalized_iso_date = (
        parsed_iso_date.strftime(
            "%Y-%m-%d"
        )
    )

    return (
        normalized_display_date,
        normalized_iso_date,
        magazine,
    )


# ============================================================
# METADATA FACTORY
# ============================================================

def build_publication_metadata(pro: bool = False) -> PublicationMetadata:
    """
    Create one shared metadata object from INPUT.json.

    The entered publication date controls:
    - the month and year shown in both PDF headers;
    - the magazine-specific edition code (UAK-YMA-YYMM / UAK-KMA-YYMM).
    The original ISO date remains available for internal records.
    """

    (
        publication_date,
        publication_date_iso,
        magazine,
    ) = _load_input_metadata()

    parsed_date = datetime.strptime(
        publication_date_iso,
        "%Y-%m-%d",
    )

    # Monthly publications use YYMM, without a day component.
    edition_code = (
        f"{EDITION_PREFIX}-"
        f"{'YMA' if magazine == 'yojana' else 'KMA'}-"
        f"{parsed_date.strftime('%y%m')}"
    )

    if pro:
        edition_code = edition_code.rsplit("-", 1)[0] + "-PRO-" + parsed_date.strftime("%y%m")

    return PublicationMetadata(
        project_name=PROJECT_NAME,
        project_version=PROJECT_VERSION,
        title=f"{magazine.upper()} MONTHLY ANCHOR" + (" - PRO" if pro else ""),
        subtitle=PUBLICATION_SUBTITLE,
        footer_brand=PUBLICATION_SUBTITLE,
        # Header displays "September 2026" rather than "01 September 2026".
        publication_date=parsed_date.strftime("%B %Y"),
        publication_date_iso=(
            publication_date_iso
        ),
        edition_code=edition_code,
        telegram_handle=TELEGRAM_HANDLE,
        website=WEBSITE,
    )