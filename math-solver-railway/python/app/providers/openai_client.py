"""OpenAI client stub -- works without an API key by returning None/error."""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class OpenAIClient:
    """Stub wrapper around the OpenAI API.

    All methods gracefully return None when no API key is configured so
    the rest of the application can function without it.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self._client = None

        if self.api_key:
            try:
                import openai
                self._client = openai.OpenAI(api_key=self.api_key)
                logger.info("OpenAI client initialised")
            except ImportError:
                logger.warning("openai package is not installed")
            except Exception as exc:
                logger.warning("Failed to initialise OpenAI client: %s", exc)

    @property
    def available(self) -> bool:
        return self._client is not None

    def solve(self, problem: str) -> Optional[dict]:
        """Ask GPT to solve a math problem.

        Returns:
            dict with ``answer`` and ``steps`` keys, or None on failure.
        """
        if not self.available:
            return None
        try:
            response = self._client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a math tutor. Solve the problem step by step."},
                    {"role": "user", "content": problem},
                ],
                max_tokens=1024,
            )
            text = response.choices[0].message.content or ""
            return {"answer": text, "steps": [text]}
        except Exception as exc:
            logger.error("OpenAI solve failed: %s", exc)
            return None

    def ocr(self, image_b64: str) -> Optional[str]:
        """Use GPT-4 Vision to extract text from an image.

        Returns:
            Extracted text or None on failure.
        """
        if not self.available:
            return None
        try:
            response = self._client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Extract all math expressions and text from this image."},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}},
                        ],
                    }
                ],
                max_tokens=512,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            logger.error("OpenAI OCR failed: %s", exc)
            return None

    def explain(self, solution: str) -> Optional[str]:
        """Ask GPT to explain a solution in simple terms.

        Returns:
            Explanation string or None on failure.
        """
        if not self.available:
            return None
        try:
            response = self._client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Explain this math solution in simple, clear language."},
                    {"role": "user", "content": solution},
                ],
                max_tokens=512,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            logger.error("OpenAI explain failed: %s", exc)
            return None
