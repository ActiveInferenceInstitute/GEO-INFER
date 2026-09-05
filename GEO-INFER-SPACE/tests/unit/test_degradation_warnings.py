"""
Tests for graceful degradation warnings.

Verifies that optional component imports in the package __init__ emit
ImportWarning when degraded to None, and that the local statistics
computation warns when neighbor lookups fail and falls back to a
self-only neighborhood.
"""

import importlib
import sys
import warnings

import pytest

import geo_infer_space
from geo_infer_space.core.statistics import SpatialStatistics


def _reload_with_missing_module(module_name: str, attr: str):
    """Reload geo_infer_space with <module_name> forced to fail importing.

    Returns the reloaded package. Restores the module and reloads the
    package on the way out, suppressing any degradation warnings emitted
    during teardown.
    """
    key = f"geo_infer_space.{module_name}"
    saved = sys.modules.get(key)
    sys.modules[key] = None
    try:
        with pytest.warns(ImportWarning, match=f"{attr} unavailable"):
            reloaded = importlib.reload(geo_infer_space)
        assert getattr(reloaded, attr) is None
    finally:
        if saved is not None:
            sys.modules[key] = saved
        else:
            sys.modules.pop(key, None)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            importlib.reload(geo_infer_space)


class TestPackageDegradationWarnings:
    """Tests for ImportWarning on degraded package __init__ imports."""

    def test_place_analyzer_degrades_with_warning(self):
        """Failing PlaceAnalyzer import warns and degrades to None."""
        _reload_with_missing_module("place_analyzer", "PlaceAnalyzer")

    def test_spatial_utils_degrades_with_warning(self):
        """Failing SpatialUtils import warns and degrades to None."""
        _reload_with_missing_module("spatial_utils", "SpatialUtils")

    def test_gis_manager_degrades_with_warning(self):
        """Failing GISManager import warns and degrades to None."""
        _reload_with_missing_module("gis", "GISManager")


class TestNeighborLookupDegradation:
    """Tests for the neighbor-lookup fallback in local statistics."""

    def test_getis_ord_warns_and_falls_back_to_self(self, caplog):
        """Failing neighbor lookups warn and still compute self-only G*."""
        stats = SpatialStatistics()

        class FailingBackend:
            def get_cell_neighbors(self, cell, k=1):
                raise ValueError("neighborhood unavailable")

        stats.dispatcher.get_backend = lambda name: FailingBackend()

        cells = ["8928308280fffff", "8928308283fffff", "8928308285fffff"]
        values = [1.0, 2.0, 3.0]

        with caplog.at_level("WARNING", logger="geo_infer_space.core.statistics"):
            result = stats.getis_ord_g(cells, values)

        assert any(
            "Neighbor lookup failed" in record.message
            and "self-only" in record.message
            for record in caplog.records
        )
        assert "g_stars" in result
        assert set(result["g_stars"].keys()) == set(cells)
