"""
API client for GEO-INFER-ACT.
"""
from typing import Dict, Any, Optional
import requests


class Client:
    """REST API client for GEO-INFER-ACT."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        
    def create_model(self, model_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new model via API."""
        response = requests.post(f"{self.base_url}/models", json=model_config)
        return response.json()
        
    def get_model(self, model_id: str) -> Dict[str, Any]:
        """Get model details via API."""
        response = requests.get(f"{self.base_url}/models/{model_id}")
        return response.json() 