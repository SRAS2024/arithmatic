"""Mathpix OCR client stub -- works without credentials by returning None."""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class MathpixClient:
    """Stub wrapper around the Mathpix OCR API.

    Returns None when no credentials are configured.
    """

    def __init__(
        self,
        app_id: Optional[str] = None,
        app_key: Optional[str] = None,
    ):
        self.app_id = app_id or os.getenv("MATHPIX_APP_ID", "")
        self.app_key = app_key or os.getenv("MATHPIX_APP_KEY", "")
        self._available = bool(self.app_id and self.app_key)
        if not self._available:
            logger.info("Mathpix credentials not configured; client disabled")

    @property
    def available(self) -> bool:
        return self._available

    def recognize(self, image_b64: str) -> Optional[dict]:
        """Send a base64-encoded image to Mathpix for math OCR.

        Args:
            image_b64: Base64-encoded image (no data-URI prefix).

        Returns:
            dict with ``latex``, ``text``, and ``confidence`` keys,
            or None on failure.
        """
        if not self._available:
            return None

        try:
            import urllib.request
            import json

            url = "https://api.mathpix.com/v3/text"
            payload = json.dumps({
                "src": f"data:image/png;base64,{image_b64}",
                "formats": ["latex_styled", "text"],
                "data_options": {"include_asciimath": True},
            }).encode()

            req = urllib.request.Request(
                url,
                data=payload,
                method="POST",
                headers={
                    "Content-Type": "application/json",
                    "app_id": self.app_id,
                    "app_key": self.app_key,
                },
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())

            return {
                "latex": data.get("latex_styled", ""),
                "text": data.get("text", ""),
                "confidence": data.get("confidence", 0.0),
            }
        except Exception as exc:
            logger.error("Mathpix recognize failed: %s", exc)
            return None
