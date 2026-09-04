"""
Pytest configuration for GEO-INFER-API tests.
"""
import os
import sys
import pytest
from fastapi.testclient import TestClient

# The application fails closed without a signing key (get_settings raises
# RuntimeError when SECRET_KEY is unset); provide a test value before any
# geo_infer_api module is imported.
os.environ.setdefault("SECRET_KEY", "test_secret_key_for_pytest_suite")

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from geo_infer_api.app import main_app
from geo_infer_api.core.config import get_settings
from geo_infer_api.endpoints.geojson_router import POLYGON_FEATURES


@pytest.fixture
def client():
    """Create a test client for FastAPI."""
    return TestClient(main_app)


@pytest.fixture
def settings():
    """Get application settings."""
    return get_settings()


@pytest.fixture
def secret_key_env():
    """Return the test SECRET_KEY value used by the suite."""
    return os.environ["SECRET_KEY"]


@pytest.fixture(autouse=True)
def clear_polygon_features():
    """Clear the polygon features dictionary before and after each test."""
    POLYGON_FEATURES.clear()
    yield
    POLYGON_FEATURES.clear()
