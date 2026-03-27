"""Tesseract OCR wrapper with graceful fallback."""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import pytesseract
    from pytesseract import Output
    _TESSERACT_AVAILABLE = True
except ImportError:
    _TESSERACT_AVAILABLE = False

try:
    from PIL import Image
except ImportError:
    Image = None


class TesseractClient:
    """Thin wrapper around pytesseract with availability checks."""

    def __init__(self, tesseract_cmd: Optional[str] = None, lang: str = "eng"):
        self.lang = lang
        self._available = False

        if not _TESSERACT_AVAILABLE:
            logger.warning("pytesseract package is not installed")
            return

        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

        # Probe whether the tesseract binary is reachable
        try:
            pytesseract.get_tesseract_version()
            self._available = True
        except Exception as exc:
            logger.warning("Tesseract binary not found: %s", exc)

    @property
    def available(self) -> bool:
        return self._available

    def ocr(self, image, config: str = "") -> dict:
        """Run OCR on a PIL Image.

        Args:
            image: PIL Image object.
            config: Extra tesseract config flags.

        Returns:
            dict with keys ``text`` (str) and ``confidence`` (float 0-1).
        """
        if not self._available:
            return {"text": "", "confidence": 0.0}

        try:
            # Get detailed data for confidence
            data = pytesseract.image_to_data(
                image, lang=self.lang, config=config, output_type=Output.DICT
            )

            # Compute mean confidence from word-level confidences
            confidences = [
                int(c) for c in data.get("conf", []) if str(c).lstrip("-").isdigit() and int(c) >= 0
            ]
            mean_conf = (sum(confidences) / len(confidences) / 100.0) if confidences else 0.0

            # Also get plain text
            text = pytesseract.image_to_string(image, lang=self.lang, config=config).strip()

            return {"text": text, "confidence": round(mean_conf, 4)}
        except Exception as exc:
            logger.error("Tesseract OCR failed: %s", exc)
            return {"text": "", "confidence": 0.0}
