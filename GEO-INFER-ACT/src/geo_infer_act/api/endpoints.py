"""
API endpoints for GEO-INFER-ACT.
"""
from typing import Dict


def create_endpoints() -> Dict[str, str]:
    """Create API endpoint definitions."""
    return {
        "models": "/models",
        "beliefs": "/models/{model_id}/beliefs",
        "policies": "/models/{model_id}/policies"
    } 