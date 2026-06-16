"""Compatibility shim for agent configuration form definitions.

The original project documentation references this module as a UI form
component. In the Python package surface, provide a minimal
interoperable data model so imports remain valid while keeping the actual
frontend form implementation in frontend-specific tooling when introduced.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional


@dataclass
class AgentConfigForm:
    """Container describing an agent configuration form payload.

    This keeps ``geo_infer_app`` imports operational and provides a structured
    configuration object for programmatic callers.
    """

    schema: Dict[str, Any]
    initial_values: Dict[str, Any]
    on_submit: Optional[Callable[[Dict[str, Any]], Any]] = None
    on_cancel: Optional[Callable[[], Any]] = None
    is_loading: bool = False
    error: Optional[str] = None

    def __init__(
        self,
        schema: Dict[str, Any],
        initialValues: Optional[Dict[str, Any]] = None,
        onSubmit: Optional[Callable[[Dict[str, Any]], Any]] = None,
        onCancel: Optional[Callable[[], Any]] = None,
        isLoading: bool = False,
        error: Optional[str] = None,
        *,
        initial_values: Optional[Dict[str, Any]] = None,
        on_submit: Optional[Callable[[Dict[str, Any]], Any]] = None,
        on_cancel: Optional[Callable[[], Any]] = None,
        is_loading: Optional[bool] = None,
    ) -> None:
        self.schema = schema
        self.initial_values = (
            initial_values if initial_values is not None else initialValues or {}
        )
        self.on_submit = on_submit if on_submit is not None else onSubmit
        self.on_cancel = on_cancel if on_cancel is not None else onCancel
        self.is_loading = is_loading if is_loading is not None else isLoading
        self.error = error

    @property
    def initialValues(self) -> Dict[str, Any]:
        """Legacy camelCase alias retained for compatibility."""
        return self.initial_values

    @initialValues.setter
    def initialValues(self, value: Dict[str, Any]) -> None:
        self.initial_values = value

    @property
    def onSubmit(self) -> Optional[Callable[[Dict[str, Any]], Any]]:
        """Legacy camelCase alias retained for compatibility."""
        return self.on_submit

    @onSubmit.setter
    def onSubmit(self, value: Optional[Callable[[Dict[str, Any]], Any]]) -> None:
        self.on_submit = value

    @property
    def onCancel(self) -> Optional[Callable[[], Any]]:
        """Legacy camelCase alias retained for compatibility."""
        return self.on_cancel

    @onCancel.setter
    def onCancel(self, value: Optional[Callable[[], Any]]) -> None:
        self.on_cancel = value

    @property
    def isLoading(self) -> bool:
        """Legacy camelCase alias retained for compatibility."""
        return self.is_loading

    @isLoading.setter
    def isLoading(self, value: bool) -> None:
        self.is_loading = value

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
