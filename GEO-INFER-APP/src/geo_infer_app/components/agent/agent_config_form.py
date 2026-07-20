"""Data model for an agent configuration form."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional


@dataclass
class AgentConfigForm:
    """Container describing an agent configuration form payload."""

    schema: Dict[str, Any]
    initial_values: Dict[str, Any]
    on_submit: Optional[Callable[[Dict[str, Any]], Any]] = None
    on_cancel: Optional[Callable[[], Any]] = None
    is_loading: bool = False
    error: Optional[str] = None

    def submit(self, values: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """Submit a normalized configuration payload."""
        payload = dict(self.initial_values)
        if values:
            payload.update(values)
        if self.on_submit is None:
            return payload
        return self.on_submit(payload)

    def cancel(self) -> Optional[Any]:
        """Execute the optional cancellation handler."""
        if self.on_cancel is None:
            return None
        return self.on_cancel()
