"""PDF processing service -- text extraction with OCR fallback."""

import io
import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from PyPDF2 import PdfReader
    _PYPDF2_AVAILABLE = True
except ImportError:
    _PYPDF2_AVAILABLE = False
    PdfReader = None

try:
    from PIL import Image
    _PIL_AVAILABLE = True
except ImportError:
    _PIL_AVAILABLE = False


class PDFService:
    """Extract text (and detect math) from PDF files."""

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract_text(self, pdf_bytes: bytes) -> dict:
        """Extract text from raw PDF bytes.

        Returns:
            dict with ``pages`` (list of page dicts) and ``total_pages``.
        """
        result: dict = {"pages": [], "total_pages": 0, "error": None}

        if not _PYPDF2_AVAILABLE:
            result["error"] = "PyPDF2 is not installed"
            return result

        try:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            total = len(reader.pages)
            result["total_pages"] = total

            for idx, page in enumerate(reader.pages):
                page_text = ""
                try:
                    page_text = page.extract_text() or ""
                except Exception as exc:
                    logger.warning("Text extraction failed for page %d: %s", idx + 1, exc)

                ocr_text = None
                # If very little text was extracted, try OCR fallback
                if len(page_text.strip()) < 20:
                    ocr_text = self._ocr_page(pdf_bytes, idx)

                display_text = page_text.strip() if page_text.strip() else (ocr_text or "")
                has_math = self.contains_math(display_text)

                result["pages"].append({
                    "page_num": idx + 1,
                    "text": display_text,
                    "has_math": has_math,
                    "ocr_text": ocr_text,
                })
        except Exception as exc:
            result["error"] = f"Failed to process PDF: {exc}"

        return result

    def process_pdf(self, file_path: str) -> dict:
        """Process a PDF file on disk.

        This is the entry point used by the /pdf route.
        """
        try:
            with open(file_path, "rb") as f:
                pdf_bytes = f.read()
        except Exception as exc:
            return {"pages": [], "total_pages": 0, "error": f"Cannot read file: {exc}"}

        return self.extract_text(pdf_bytes)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def contains_math(text: str) -> bool:
        """Return True if *text* likely contains mathematical content."""
        if not text:
            return False
        math_patterns = [
            r"\d+\s*[+\-*/^]\s*\d+",         # basic arithmetic
            r"[=<>]",                           # equations / inequalities
            r"\bx\s*[\^]",                      # x^n
            r"\d+\s*x",                         # coefficients
            r"\bsqrt\b",                        # square root
            r"\b(sin|cos|tan|log|ln)\b",        # trig / log
            r"\bintegral\b|\bderivative\b",     # calculus keywords
            r"\blim\b",                         # limits
            r"\bmatrix\b",                      # linear algebra
            r"\bsolve\b",                       # solve keyword
            r"\bfrac\b",                        # fraction
            r"\\frac\{",                        # LaTeX fraction
            r"\bsum\b.*=",                      # summation
        ]
        for pat in math_patterns:
            if re.search(pat, text, re.IGNORECASE):
                return True
        return False

    # ------------------------------------------------------------------
    # OCR fallback for scanned / image-based pages
    # ------------------------------------------------------------------

    def _ocr_page(self, pdf_bytes: bytes, page_index: int) -> Optional[str]:
        """Try to OCR a single page rendered as an image.

        Uses pdf2image (poppler) if available, otherwise returns None.
        """
        try:
            from pdf2image import convert_from_bytes
            images = convert_from_bytes(
                pdf_bytes,
                first_page=page_index + 1,
                last_page=page_index + 1,
                dpi=200,
            )
            if not images:
                return None
            img = images[0]

            try:
                import pytesseract
                text = pytesseract.image_to_string(img, config="--psm 6")
                return text.strip() if text else None
            except ImportError:
                logger.debug("pytesseract not available for OCR fallback")
                return None
        except ImportError:
            logger.debug("pdf2image not available for OCR fallback")
            return None
        except Exception as exc:
            logger.warning("OCR fallback failed for page %d: %s", page_index + 1, exc)
            return None
