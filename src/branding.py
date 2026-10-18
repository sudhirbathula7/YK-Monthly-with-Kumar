from __future__ import annotations

# ============================================================
# BRAND IDENTITY — shared umbrella brand
# ============================================================

BRAND_NAME = "UPSC Anchor with Kumar"
BRAND_SHORT_NAME = "UPSC Anchor"
BRAND_AUTHOR = "Kumar"

# Internal project/folder identity; not the public-facing brand.
PROJECT_SERIES_NAME = "YK Monthly with Kumar"

# ============================================================
# MONTHLY PUBLICATIONS
# ============================================================

PUBLICATION_TITLE = "MONTHLY UPSC ANCHOR"
PUBLICATION_SUBTITLE = BRAND_NAME

YOJANA_SERIES_TITLE = "YOJANA STUDY SERIES"
KURUKSHETRA_SERIES_TITLE = "KURUKSHETRA STUDY SERIES"

NORMAL_EDITION_TITLE = "NORMAL EDITION"
PRO_EDITION_TITLE = "PRO EDITION"

MAGAZINE_SERIES_TITLES = {
    "yojana": YOJANA_SERIES_TITLE,
    "kurukshetra": KURUKSHETRA_SERIES_TITLE,
}

EDITION_TITLES = {
    "normal": NORMAL_EDITION_TITLE,
    "pro": PRO_EDITION_TITLE,
}


def get_series_title(magazine: str) -> str:
    """Return the public-facing series title for a supported magazine."""
    key = magazine.strip().lower()
    if key not in MAGAZINE_SERIES_TITLES:
        raise ValueError(f"Unsupported magazine: {magazine!r}")
    return MAGAZINE_SERIES_TITLES[key]


def get_edition_title(edition: str) -> str:
    """Return the public-facing label for a supported edition."""
    key = edition.strip().lower()
    if key not in EDITION_TITLES:
        raise ValueError(f"Unsupported edition: {edition!r}")
    return EDITION_TITLES[key]


TAGLINE = "Understand the issue. Recall the argument."
COPYRIGHT_TEXT = f"© 2026 {BRAND_NAME}"

# ============================================================
# PUBLIC CHANNELS
# ============================================================

TELEGRAM_HANDLE = "@upscanchorwithkumar"
WEBSITE = ""
YOUTUBE = ""