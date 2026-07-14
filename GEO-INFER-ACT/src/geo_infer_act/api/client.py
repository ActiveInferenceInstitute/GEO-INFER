"""
API client for GEO-INFER-ACT.
"""

from typing import Any, Dict
from urllib.parse import quote
import requests


class Client:
    """REST API client for GEO-INFER-ACT."""

    def __init__(self, base_url: str = "http://localhost:8000", timeout: float = 10.0):
        if timeout <= 0:
            raise ValueError("timeout must be greater than zero")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _request(self, method: str, path: str, **kwargs: Any) -> Dict[str, Any]:
        """Execute a bounded request and raise for non-success responses."""
        response = requests.request(
            method,
            f"{self.base_url}{path}",
            timeout=self.timeout,
            **kwargs,
        )
        response.raise_for_status()
        return response.json()

    def create_model(self, model_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new model via API."""
        return self._request("POST", "/models", json=model_config)

    def get_model(self, model_id: str) -> Dict[str, Any]:
        """Get model details via API."""
        return self._request("GET", f"/models/{quote(str(model_id), safe='')}")
