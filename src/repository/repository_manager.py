"""Minimal monthly PDF output and source-text archive paths.

Student PDFs: output/<magazine>/<year>/<edition>.pdf
Original input: repository/<year>/<month>/<edition>_INPUT_DATA.txt
"""
from __future__ import annotations

import re
import calendar
import shutil
from pathlib import Path
from typing import Any

from src.config import PROJECT_ROOT
from src.publication import PublicationMetadata


def _edition_parts(metadata: PublicationMetadata) -> tuple[str, str, str, str]:
    edition = metadata.edition_code.strip().upper()
    match = re.fullmatch(r"UAK-(YMA|KMA)-(\d{2})(0[1-9]|1[0-2])", edition)
    if not match:
        raise ValueError(
            f"Invalid edition code {edition!r}; expected UAK-YMA-YYMM or UAK-KMA-YYMM"
        )
    magazine = "Yojana" if match.group(1) == "YMA" else "Kurukshetra"
    year = f"20{match.group(2)}"
    month = match.group(3)
    return edition, magazine, year, month


def build_yearly_archive_directory(metadata: PublicationMetadata) -> Path:
    """Return the PDF destination, with no preview or month subfolder."""
    _, magazine, year, _ = _edition_parts(metadata)
    folder = PROJECT_ROOT / "output" / magazine / year
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def build_repository_archive_directory(metadata: PublicationMetadata) -> Path:
    """Return the repository year/month folder for original input text."""
    _, _, year, month = _edition_parts(metadata)
    month_folder = f"{month}_{calendar.month_name[int(month)]}"
    folder = PROJECT_ROOT / "repository" / year / month_folder
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def complete_repository_and_archive(
    *,
    metadata: PublicationMetadata,
    standard_pdf: Path,
    pro_pdf: Path,
    elapsed_seconds: float | None = None,
) -> dict[str, Any]:
    """Keep the two PDFs in output and one source text in repository.

    Does not delete existing legacy archives, indexes or previews.
    """
    edition, _, _, _ = _edition_parts(metadata)
    pdf_directory = build_yearly_archive_directory(metadata)
    archive_directory = build_repository_archive_directory(metadata)
    expected_pdf = pdf_directory / f"{edition}.pdf"
    expected_pro = pdf_directory / f"{edition}_pro.pdf"
    for source, destination in ((Path(standard_pdf), expected_pdf), (Path(pro_pdf), expected_pro)):
        if not source.is_file():
            raise FileNotFoundError(f"Generated PDF missing: {source}")
        if source.resolve() != destination.resolve():
            shutil.copy2(source, destination)

    input_source = PROJECT_ROOT / "INPUT_DATA.txt"
    if not input_source.is_file():
        raise FileNotFoundError(f"Source text missing: {input_source}")
    input_file = archive_directory / f"{edition}_INPUT_DATA.txt"
    shutil.copy2(input_source, input_file)
    return {
        "archive_directory": archive_directory,
        "pdf_directory": pdf_directory,
        "input_file": input_file,
    }
