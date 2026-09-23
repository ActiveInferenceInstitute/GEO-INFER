"""
Tests for the geo_infer_space package import contract and the local
statistics degradation fallback.

The package __init__ imports PlaceAnalyzer, SpatialUtils, and GISManager
unconditionally (RISK-policy fail-fast, GS19-82): these components depend
only on declared hard dependencies, so a broken internal import is a
packaging bug that must propagate instead of silently nulling the public
API. On a healthy install the package must resolve every declared export.

The neighbor-lookup fallback in geo_infer_space.core.statistics still
degrades gracefully: a failing backend warns and computes a self-only
neighborhood.
"""

import importlib
import importlib.util
import sys

import pytest

import geo_infer_space
from geo_infer_space.core.statistics import SpatialStatistics


class _RaisingLoader:
    """Loader whose exec_module raises, simulating a broken submodule."""

    def create_module(self, spec):
        return None  # default module creation

    def exec_module(self, module):
        raise ImportError(f"simulated broken import: {module.__spec__.name}")


class _RaisingFinder:
    """meta_path finder routing exactly one module to _RaisingLoader."""

    def __init__(self, target):
        self._target = target

    def find_spec(self, fullname, path=None, target=None):
        if fullname != self._target:
            return None
        return importlib.util.spec_from_loader(fullname, _RaisingLoader())


class TestPackageImportContract:
    """Tests for the unconditional-import (fail-fast) package contract."""

    def test_healthy_install_resolves_all_exports(self):
        """A healthy install resolves every declared public export."""
        for name in geo_infer_space.__all__:
            assert getattr(geo_infer_space, name) is not None
        # The previously-optional components are real classes now.
        for name in ("PlaceAnalyzer", "SpatialUtils", "GISManager"):
            assert isinstance(getattr(geo_infer_space, name), type)

    @pytest.mark.parametrize(
        ("module_name", "attr"),
        [
            ("place_analyzer", "PlaceAnalyzer"),
            ("spatial_utils", "SpatialUtils"),
            ("gis", "GISManager"),
        ],
    )
    def test_broken_internal_import_propagates(self, monkeypatch, module_name, attr):
        """A broken internal import raises instead of silently nulling the API.

        Removes the cached submodule and installs a meta_path finder whose
        loader raises during exec_module, so the reload exercises a real
        failure routed through the import system -- without ever placing
        None in sys.modules.
        """
        key = f"geo_infer_space.{module_name}"
        monkeypatch.delitem(sys.modules, key)
        monkeypatch.setattr(sys, "meta_path", [_RaisingFinder(key), *sys.meta_path])

        with pytest.raises(ImportError, match="simulated broken import"):
            importlib.reload(geo_infer_space)

        # Fail-fast: the failure propagated; the package did not respond
        # by nulling out its previously imported public API.
        assert getattr(geo_infer_space, attr) is not None


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
            "Neighbor lookup failed" in record.message and "self-only" in record.message
            for record in caplog.records
        )
        assert "g_stars" in result
        assert set(result["g_stars"].keys()) == set(cells)
