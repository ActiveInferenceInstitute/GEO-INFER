"""Regression tests for generic spatial context analysis."""

import numpy as np
import pytest

from geo_infer_space.core.analytics import SpatialAnalyticsInterface


def test_analyze_context_resolves_h3_cell():
    """Context analysis should use the configured backend's indexing API."""
    analytics = SpatialAnalyticsInterface(backend="h3")

    result = analytics.analyze_context(
        {"position": np.array([37.7749, -122.4194]), "resolution": 8}
    )

    assert result["status"] == "analyzed"
    assert isinstance(result["cell"], str)


def test_analyze_context_rejects_non_mapping_input():
    """Context analysis should fail clearly for invalid input types."""
    analytics = SpatialAnalyticsInterface(backend="h3")

    with pytest.raises(TypeError, match="context must be a dictionary"):
        analytics.analyze_context([37.7749, -122.4194])
