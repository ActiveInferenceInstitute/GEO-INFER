"""Deterministic integration registry for GEO-INFER-ANT."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class IntegrationManager:
    """Record configured integrations and expose their readiness state."""

    integrations: Dict[str, Any] = field(default_factory=dict)

    def setup_integrations(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and store integration configuration."""
        if not isinstance(config, dict):
            raise TypeError("Integration configuration must be a mapping")
        self.integrations = dict(config)
        return dict(self.integrations)

    def is_enabled(self, name: str) -> bool:
        """Return whether a named integration is explicitly enabled."""
        value = self.integrations.get(name, False)
        return bool(value.get("enabled", False)) if isinstance(value, dict) else bool(value)


__all__ = ["IntegrationManager"]
