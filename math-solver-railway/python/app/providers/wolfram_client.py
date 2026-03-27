"""Wolfram Alpha client stub -- works without an APP_ID by returning None."""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class WolframClient:
    """Stub wrapper around the Wolfram Alpha API.

    Returns None when no WOLFRAM_APP_ID is configured.
    """

    def __init__(self, app_id: Optional[str] = None):
        self.app_id = app_id or os.getenv("WOLFRAM_APP_ID", "")
        self._available = bool(self.app_id)
        if not self._available:
            logger.info("Wolfram Alpha APP_ID not configured; client disabled")

    @property
    def available(self) -> bool:
        return self._available

    def query(self, expression: str) -> Optional[dict]:
        """Query Wolfram Alpha with a math expression.

        Args:
            expression: Math expression or natural-language query.

        Returns:
            dict with ``result`` and ``pods`` keys, or None on failure.
        """
        if not self._available:
            return None

        try:
            import urllib.request
            import urllib.parse
            import json

            encoded = urllib.parse.quote(expression)
            url = (
                f"https://api.wolframalpha.com/v2/query"
                f"?input={encoded}&appid={self.app_id}&output=json"
            )
            req = urllib.request.Request(url, headers={"User-Agent": "ArithmeticSolver/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())

            query_result = data.get("queryresult", {})
            pods = query_result.get("pods", [])
            result_text = ""
            for pod in pods:
                if pod.get("id") == "Result" or pod.get("title") == "Result":
                    subpods = pod.get("subpods", [])
                    if subpods:
                        result_text = subpods[0].get("plaintext", "")
                    break

            return {"result": result_text, "pods": pods}
        except Exception as exc:
            logger.error("Wolfram query failed: %s", exc)
            return None
