from __future__ import annotations

import os
import time
from pathlib import Path

from src.pdf.font_loader import register_fonts
from src.pdf.pdf_generator import generate_pdf
from src.pdf.pro_pdf_generator import generate_pro_pdf
from src.publication import build_publication_metadata
from src.repository.repository_manager import (
    complete_repository_and_archive,
    build_yearly_archive_directory,
)


# ============================================================
# DEVELOPMENT SETTINGS
# ============================================================

OPEN_PDF = True
OPEN_PRO_PDF = True


# ============================================================
# OPEN GENERATED FILE
# ============================================================

def open_generated_file(
    file_path: Path,
) -> None:
    if not file_path.exists():
        return

    if os.name == "nt":
        os.startfile(
            file_path.resolve()
        )


# ============================================================
# OUTPUT FILENAMES
# ============================================================

def build_output_filenames(edition_code: str) -> tuple[str, str]:
    """Use the publication edition ID for both monthly PDF filenames."""
    edition_id = edition_code.strip()
    if not edition_id or "/" in edition_id or chr(92) in edition_id:
        raise ValueError(f"Invalid edition code for output filename: {edition_code!r}")
    return f"{edition_id}.pdf", f"{edition_id}_pro.pdf"


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    production_started_at = (
        time.perf_counter()
    )

    # Register fonts once.
    register_fonts()

    # One metadata object for the complete run.
    metadata = (
        build_publication_metadata()
    )

    (
        standard_pdf_filename,
        pro_pdf_filename,
    ) = build_output_filenames(
        metadata.edition_code
    )

    pdf_directory = build_yearly_archive_directory(metadata)

    # ========================================================
    # STANDARD PDF
    # ========================================================

    pdf_output_file = (
        pdf_directory
        / standard_pdf_filename
    )

    generated_pdf = generate_pdf(
        output_path=pdf_output_file,
        metadata=metadata,
    )

    print()
    print("=" * 60)
    print("STANDARD PDF GENERATED SUCCESSFULLY")
    print("=" * 60)
    print(
        f"Date   : {metadata.publication_date}"
    )
    print(
        f"Edition: {metadata.edition_code}"
    )
    print(
        f"Output : {generated_pdf.resolve()}"
    )
    print("=" * 60)

    # ========================================================
    # PRO PDF
    # ========================================================

    pro_output_file = (
        pdf_directory
        / pro_pdf_filename
    )

    generated_pro_pdf = generate_pro_pdf(
        output_path=pro_output_file,
        metadata=metadata,
    )

    print()
    print("=" * 60)
    print("PRO PDF GENERATED SUCCESSFULLY")
    print("=" * 60)
    print(
        f"Date   : {metadata.publication_date}"
    )
    print(
        f"Edition: {metadata.edition_code}"
    )
    print(
        f"Output : {generated_pro_pdf.resolve()}"
    )
    print("=" * 60)

    # ========================================================
    # REPOSITORY + YEARLY MAGAZINE ARCHIVE
    # ========================================================

    elapsed_seconds = (
        time.perf_counter()
        - production_started_at
    )

    repository_result = (
        complete_repository_and_archive(
            metadata=metadata,
            standard_pdf=generated_pdf,
            pro_pdf=generated_pro_pdf,
            elapsed_seconds=elapsed_seconds,
        )
    )

    archive_directory = repository_result["archive_directory"]
    pdf_directory = repository_result["pdf_directory"]

    print()
    print("=" * 60)
    print("PDFS AND SOURCE TEXT SAVED")
    print("=" * 60)
    print(f"PDF folder : {pdf_directory.resolve()}")
    print(f"Input file : {repository_result['input_file'].resolve()}")
    print("=" * 60)

    # ========================================================
    # OPEN BOTH PDFS
    # ========================================================

    if OPEN_PDF:
        open_generated_file(
            generated_pdf
        )

    if OPEN_PRO_PDF:
        open_generated_file(
            generated_pro_pdf
        )


if __name__ == "__main__":
    main()