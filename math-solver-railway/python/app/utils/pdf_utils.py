"""PDF utility functions for extraction and validation."""

import io
from typing import Optional

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None


def extract_pages_text(pdf_bytes: bytes) -> list[str]:
    """Extract text from each page of a PDF.

    Args:
        pdf_bytes: Raw PDF file bytes.

    Returns:
        List of strings, one per page.
    """
    if PdfReader is None:
        raise RuntimeError("PyPDF2 is not installed")
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        pages = []
        for page in reader.pages:
            text = page.extract_text() or ""
            pages.append(text)
        return pages
    except Exception as exc:
        raise ValueError(f"Failed to read PDF: {exc}") from exc


def count_pages(pdf_bytes: bytes) -> int:
    """Count the number of pages in a PDF.

    Args:
        pdf_bytes: Raw PDF file bytes.

    Returns:
        Number of pages.
    """
    if PdfReader is None:
        raise RuntimeError("PyPDF2 is not installed")
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        return len(reader.pages)
    except Exception:
        return 0


def is_valid_pdf(data: bytes) -> bool:
    """Check whether data represents a valid PDF file.

    Args:
        data: Raw bytes to check.

    Returns:
        True if the data can be parsed as a PDF.
    """
    if not data or len(data) < 5:
        return False
    # PDF files start with %PDF
    if not data[:5].startswith(b"%PDF"):
        return False
    if PdfReader is None:
        # Cannot fully validate without PyPDF2; trust the header
        return True
    try:
        reader = PdfReader(io.BytesIO(data))
        _ = len(reader.pages)
        return True
    except Exception:
        return False
