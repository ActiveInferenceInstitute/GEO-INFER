"""Regression tests for generic spatial context analysis."""

import numpy as np
import pytest

from geo_infer_space.core.analytics import SpatialAnalyticsInterface
from geo_infer_space.core.interfaces import UnsupportedSpatialOperationError


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


def test_unsupported_facade_operations_use_a_typed_error():
    """Unimplemented public operations have a stable, inspectable error type."""
    analytics = SpatialAnalyticsInterface(backend="h3")

    calls = {
        "analyze_network": ([],),
        "detect_patterns": ({},),
        "compute_density": ([],),
        "analyze_accessibility": ([], []),
    }
    for operation, args in calls.items():
        with pytest.raises(UnsupportedSpatialOperationError) as error:
            getattr(analytics, operation)(*args)
        assert error.value.operation == operation
        assert error.value.backend == "h3"
