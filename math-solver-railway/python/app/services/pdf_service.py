"""
PDF Service - Extract text and math from PDF documents.
"""
import io
import re
from typing import Optional


class PDFService:
    """Process PDF documents: text extraction, OCR fallback, math detection."""

    @staticmethod
    def extract_text(pdf_bytes: bytes) -> dict:
        """Extract text from PDF bytes.

        Returns dict with: pages, total_pages, error
        """
        if pdf_bytes is None:
            return {'error': 'No PDF data provided', 'pages': [], 'total_pages': 0}

        result = {
            'pages': [],
            'total_pages': 0,
            'error': None
        }

        # Try PyPDF2 text extraction first
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            result['total_pages'] = len(reader.pages)

            for i, page in enumerate(reader.pages):
                page_text = page.extract_text() or ''
                has_math = PDFService.contains_math(page_text)

                page_data = {
                    'page_num': i + 1,
                    'text': page_text.strip(),
                    'has_math': has_math,
                    'ocr_text': '',
                    'extraction_method': 'text_layer'
                }

                # If no text extracted, try OCR fallback
                if not page_text.strip():
                    ocr_text = PDFService._ocr_page(pdf_bytes, i)
                    if ocr_text:
                        page_data['text'] = ocr_text
                        page_data['ocr_text'] = ocr_text
                        page_data['has_math'] = PDFService.contains_math(ocr_text)
                        page_data['extraction_method'] = 'ocr'

                result['pages'].append(page_data)

        except Exception as e:
            result['error'] = f'PDF processing failed: {e}'
            # Try OCR-only approach
            try:
                ocr_pages = PDFService._ocr_all_pages(pdf_bytes)
                if ocr_pages:
                    result['pages'] = ocr_pages
                    result['total_pages'] = len(ocr_pages)
                    result['error'] = None
            except Exception as e2:
                result['error'] = f'PDF processing and OCR both failed: {e}; {e2}'

        return result

    @staticmethod
    def _ocr_page(pdf_bytes: bytes, page_num: int) -> Optional[str]:
        """OCR a single page of a PDF."""
        try:
            from pdf2image import convert_from_bytes
            import pytesseract

            images = convert_from_bytes(
                pdf_bytes,
                first_page=page_num + 1,
                last_page=page_num + 1,
                dpi=300
            )

            if images:
                text = pytesseract.image_to_string(images[0], config='--psm 6')
                return text.strip()
        except ImportError:
            pass
        except Exception:
            pass
        return None

    @staticmethod
    def _ocr_all_pages(pdf_bytes: bytes) -> list:
        """OCR all pages of a PDF."""
        pages = []
        try:
            from pdf2image import convert_from_bytes
            import pytesseract

            images = convert_from_bytes(pdf_bytes, dpi=200)

            for i, img in enumerate(images):
                text = pytesseract.image_to_string(img, config='--psm 6')
                has_math = PDFService.contains_math(text)
                pages.append({
                    'page_num': i + 1,
                    'text': text.strip(),
                    'has_math': has_math,
                    'ocr_text': text.strip(),
                    'extraction_method': 'ocr'
                })
        except ImportError:
            pass
        except Exception:
            pass
        return pages

    @staticmethod
    def contains_math(text: str) -> bool:
        """Check if text contains mathematical content."""
        if not text:
            return False

        math_patterns = [
            r'[=+\-*/^]',           # Basic operators
            r'\d+\s*[+\-*/^]\s*\d+', # Expressions like 2+3
            r'[a-z]\s*[=<>]',        # Variable equations
            r'x\^?\d',               # x^2, x2
            r'\\frac',               # LaTeX fractions
            r'\\sqrt',               # LaTeX square root
            r'sqrt\(',               # sqrt function
            r'sin|cos|tan|log|ln',   # Math functions
            r'∫|∑|∏|√|π',           # Unicode math symbols
            r'integral|derivative|differentiate|integrate',
            r'solve|factor|simplify|expand',
            r'matrix|determinant|eigenvalue',
            r'limit|lim\s',
            r'probability|P\s*\(',
            r'mean|median|std|variance',
        ]

        for pattern in math_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True

        return False

    @staticmethod
    def get_math_pages(pdf_bytes: bytes) -> list:
        """Get only pages that contain math."""
        result = PDFService.extract_text(pdf_bytes)
        return [p for p in result.get('pages', []) if p.get('has_math')]

    @staticmethod
    def get_all_text(pdf_bytes: bytes) -> str:
        """Get all text from PDF as a single string."""
        result = PDFService.extract_text(pdf_bytes)
        texts = [p['text'] for p in result.get('pages', []) if p.get('text')]
        return '\n\n'.join(texts)
