"""
OCR Service - Text extraction from images using Tesseract and Pillow.
"""
import io
from typing import Optional
from PIL import Image

from app.services.image_preprocess_service import ImagePreprocessService


class OCRService:
    """Extract text from images using OCR."""

    @staticmethod
    def extract_text(image_bytes: bytes) -> dict:
        """Extract text from image bytes.

        Returns dict with: text, confidence, raw_text, latex
        """
        result = {
            'text': '',
            'raw_text': '',
            'latex': '',
            'confidence': 0.0,
            'error': None
        }

        try:
            img = Image.open(io.BytesIO(image_bytes))
        except Exception as e:
            result['error'] = f'Failed to open image: {e}'
            return result

        # Preprocess for better OCR
        try:
            processed = ImagePreprocessService.preprocess_for_ocr(img)
        except Exception:
            processed = img.convert('L') if img.mode != 'L' else img

        # Try pytesseract
        try:
            import pytesseract

            # Get detailed OCR data for confidence
            ocr_data = pytesseract.image_to_data(processed, output_type=pytesseract.Output.DICT)

            words = []
            confidences = []
            for i, word in enumerate(ocr_data['text']):
                word = word.strip()
                if word:
                    words.append(word)
                    conf = int(ocr_data['conf'][i]) if ocr_data['conf'][i] != '-1' else 0
                    if conf > 0:
                        confidences.append(conf)

            raw_text = ' '.join(words)
            avg_confidence = sum(confidences) / len(confidences) / 100.0 if confidences else 0.0

            # Also get full text extraction
            full_text = pytesseract.image_to_string(processed, config='--psm 6')

            result['raw_text'] = raw_text
            result['text'] = full_text.strip() if full_text.strip() else raw_text
            result['confidence'] = round(avg_confidence, 3)

            # Attempt math-aware post-processing
            result['latex'] = OCRService._text_to_latex(result['text'])

        except ImportError:
            result['error'] = 'pytesseract not installed'
            result['confidence'] = 0.0
        except Exception as e:
            result['error'] = f'OCR failed: {e}'
            result['confidence'] = 0.0

        return result

    @staticmethod
    def _text_to_latex(text: str) -> str:
        """Convert OCR text to LaTeX-like math notation."""
        if not text:
            return ''

        import re
        latex = text.strip()

        # Common OCR math corrections
        replacements = [
            (r'×', '*'),
            (r'÷', '/'),
            (r'−', '-'),
            (r'—', '-'),
            (r'≤', '<='),
            (r'≥', '>='),
            (r'≠', '!='),
            (r'±', '+-'),
            (r'√', 'sqrt'),
            (r'π', 'pi'),
            (r'∞', 'infinity'),
            (r'∫', 'integrate'),
            (r'∑', 'sum'),
            (r'∏', 'product'),
            (r'α', 'alpha'),
            (r'β', 'beta'),
            (r'γ', 'gamma'),
            (r'θ', 'theta'),
            (r'λ', 'lambda'),
            (r'μ', 'mu'),
            (r'σ', 'sigma'),
            (r'²', '^2'),
            (r'³', '^3'),
            (r'⁴', '^4'),
            (r'¹', '^1'),
            (r'½', '1/2'),
            (r'¼', '1/4'),
            (r'¾', '3/4'),
        ]

        for old, new in replacements:
            latex = latex.replace(old, new)

        # Clean up whitespace
        latex = re.sub(r'\s+', ' ', latex).strip()

        return latex

    def process_image(self, file_path: str, language: str = "eng", preprocess: bool = True) -> dict:
        """Process an image file on disk and return OCR results.

        This is the entry point used by the /ocr route.

        Args:
            file_path: Path to the image file on disk.
            language: Tesseract language code.
            preprocess: Whether to apply image preprocessing.

        Returns:
            dict compatible with OCRResponse.
        """
        try:
            with open(file_path, "rb") as f:
                image_bytes = f.read()
        except Exception as e:
            return {"text": "", "confidence": 0.0, "raw_text": "", "latex": "", "error": f"Cannot read file: {e}"}

        result = self.extract_text(image_bytes)

        # If preprocessing was disabled, re-run without the pipeline
        if not preprocess and result.get("error"):
            try:
                img = Image.open(io.BytesIO(image_bytes))
                import pytesseract
                text = pytesseract.image_to_string(img, lang=language)
                result["text"] = text.strip()
                result["raw_text"] = text.strip()
                result["latex"] = OCRService._text_to_latex(text.strip())
                result["error"] = None
            except Exception:
                pass

        return result

    @staticmethod
    def extract_math_regions(image_bytes: bytes) -> list:
        """Attempt to detect and extract math regions from an image.

        Returns list of dicts with {text, confidence, bbox}.
        """
        # For now, treat entire image as one region
        result = OCRService.extract_text(image_bytes)
        return [{
            'text': result['text'],
            'latex': result['latex'],
            'confidence': result['confidence'],
            'bbox': None
        }]
