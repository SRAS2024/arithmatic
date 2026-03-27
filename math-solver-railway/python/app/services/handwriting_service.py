"""
Handwriting Service - Recognize handwritten math from images.
"""
import io
import re
from PIL import Image

from app.services.image_preprocess_service import ImagePreprocessService
from app.services.ocr_service import OCRService


class HandwritingService:
    """Recognize handwritten mathematical expressions from images."""

    def recognize(self, image_bytes_or_path, language: str = "eng", enhance: bool = True) -> dict:
        """Recognize handwritten math from image bytes.

        Returns dict with: text, latex, confidence, raw_text
        """
        result = {
            'text': '',
            'latex': '',
            'confidence': 0.0,
            'raw_text': '',
            'is_handwritten': True,
            'error': None
        }

        # Accept either a file path (str) or raw bytes
        if isinstance(image_bytes_or_path, str):
            try:
                with open(image_bytes_or_path, "rb") as f:
                    image_bytes = f.read()
            except Exception as e:
                result['error'] = f'Cannot read file: {e}'
                return result
        else:
            image_bytes = image_bytes_or_path

        try:
            img = Image.open(io.BytesIO(image_bytes))
        except Exception as e:
            result['error'] = f'Failed to open image: {e}'
            return result

        # Apply handwriting-optimized preprocessing
        try:
            processed = HandwritingService._preprocess_handwriting(img)
        except Exception:
            processed = img

        # Convert back to bytes for OCR
        buf = io.BytesIO()
        if processed.mode == 'RGBA':
            processed = processed.convert('RGB')
        processed.save(buf, format='PNG')
        processed_bytes = buf.getvalue()

        # Use OCR with handwriting-specific config
        try:
            import pytesseract

            # Use PSM 6 (assume uniform block) or PSM 7 (single line)
            text = pytesseract.image_to_string(processed, config='--psm 6 --oem 3')

            # Get confidence
            data = pytesseract.image_to_data(processed, output_type=pytesseract.Output.DICT)
            confidences = [int(c) for c in data['conf'] if str(c) != '-1' and int(c) > 0]
            avg_conf = sum(confidences) / len(confidences) / 100.0 if confidences else 0.0

            # Handwriting typically has lower confidence - adjust
            adj_conf = avg_conf * 0.85  # Reduce confidence for handwriting

            result['raw_text'] = text.strip()
            result['text'] = HandwritingService._postprocess_math(text.strip())
            result['latex'] = OCRService._text_to_latex(result['text'])
            result['confidence'] = round(adj_conf, 3)

        except ImportError:
            # Fall back to basic OCR
            ocr_result = OCRService.extract_text(processed_bytes)
            result['raw_text'] = ocr_result.get('raw_text', '')
            result['text'] = ocr_result.get('text', '')
            result['latex'] = ocr_result.get('latex', '')
            result['confidence'] = ocr_result.get('confidence', 0.0) * 0.8
            result['error'] = 'pytesseract not available, using basic OCR'
        except Exception as e:
            result['error'] = f'Handwriting recognition failed: {e}'

        return result

    @staticmethod
    def _preprocess_handwriting(img: Image.Image) -> Image.Image:
        """Apply handwriting-optimized preprocessing."""
        # Convert to grayscale
        gray = ImagePreprocessService.to_grayscale(img)

        # Enhance contrast more aggressively for handwriting
        enhanced = ImagePreprocessService.enhance_contrast(gray, factor=2.5)

        # Denoise
        denoised = ImagePreprocessService.denoise(enhanced)

        # Adaptive-style thresholding (simple version)
        thresholded = ImagePreprocessService.threshold(denoised, thresh=140)

        # Resize if too small (handwriting needs decent resolution)
        w, h = thresholded.size
        if max(w, h) < 500:
            scale = 500 / max(w, h)
            new_w = int(w * scale)
            new_h = int(h * scale)
            thresholded = thresholded.resize((new_w, new_h), Image.LANCZOS)

        return thresholded

    @staticmethod
    def _postprocess_math(text: str) -> str:
        """Post-process OCR text to fix common handwriting OCR errors."""
        if not text:
            return ''

        result = text

        # Common handwriting OCR misreads
        corrections = [
            # Letters confused with numbers
            (r'\bO\b(?=\s*[+\-*/=])', '0'),  # O -> 0 in math context
            (r'\bl\b(?=\s*[+\-*/=])', '1'),   # l -> 1 in math context
            (r'\bI\b(?=\s*[+\-*/=])', '1'),   # I -> 1 in math context

            # Common symbol misreads
            (r'[xX](?=\s*[²³⁴])', 'x'),  # Ensure lowercase x for variables

            # Fix common spacing issues
            (r'(\d)\s+(\d)', r'\1\2'),  # Remove spaces between digits
            (r'([a-z])\s*\^\s*(\d)', r'\1^\2'),  # Fix spacing around powers

            # Fix equals sign misreads
            (r'\s*[—–]\s*', ' - '),  # Em/en dash to minus

            # Clean up
            (r'\s+', ' '),
        ]

        for pattern, replacement in corrections:
            result = re.sub(pattern, replacement, result)

        return result.strip()
