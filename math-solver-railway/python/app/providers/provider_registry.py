"""Central registry for optional third-party providers."""

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class ProviderRegistry:
    """Keeps track of available (and unavailable) provider instances.

    Usage::

        registry = ProviderRegistry()
        registry.register("openai", openai_client)
        client = registry.get("openai")
        available = registry.list_available()
    """

    def __init__(self):
        self._providers: dict[str, Any] = {}

    def register(self, name: str, provider: Any) -> None:
        """Register a provider by name.

        Args:
            name: Unique provider name (e.g. ``"openai"``, ``"wolfram"``).
            provider: Provider instance.  If the object exposes an
                ``available`` property it will be inspected by
                :meth:`list_available`.
        """
        self._providers[name] = provider
        logger.info("Registered provider: %s", name)

    def get(self, name: str) -> Optional[Any]:
        """Retrieve a registered provider by name.

        Returns:
            The provider instance, or ``None`` if not registered.
        """
        return self._providers.get(name)

    def list_available(self) -> list[str]:
        """Return a list of provider names that are currently available.

        A provider is considered available if:
        - It has an ``available`` attribute that is truthy, **or**
        - It does not have an ``available`` attribute (assumed available).
        """
        available = []
        for name, provider in self._providers.items():
            try:
                if hasattr(provider, "available"):
                    if provider.available:
                        available.append(name)
                else:
                    available.append(name)
            except Exception:
                pass
        return sorted(available)

    def list_all(self) -> list[str]:
        """Return names of all registered providers (available or not)."""
        return sorted(self._providers.keys())
