"""Tests for the neighborhood-fallback warning contract in H3 analytics.

When ``h3.grid_disk`` fails for a cell (e.g. a malformed or foreign index),
the analytics and backend layers fall back to a degraded neighborhood. These
tests pin that the fallback is *logged* via ``logger.warning`` rather than
happening silently, for:

- Getis-Ord Gi* (self-only neighborhood fallback)
- Local Moran's I (empty neighborhood fallback)
- Local density gradient / spatial lag (empty neighborhood fallback)
- ``H3Backend.find_clusters`` cluster expansion (empty neighbor set fallback)
"""

from __future__ import annotations

import logging

import pytest
import h3

from geo_infer_space.backends.h3.core import H3Cell, H3Grid
from geo_infer_space.backends.h3.analytics import H3DensityAnalyzer, H3SpatialAnalyzer
from geo_infer_space.backends.h3.h3_backend import H3Backend

SEED_CELL = "8928308280fffff"
INVALID_CELL = "not-a-cell"


def _grid_with_invalid_cell(n_valid: int = 5) -> H3Grid:
    """Build a grid of valid res-9 cells plus one malformed cell index."""
    valid_indices = sorted(h3.grid_disk(SEED_CELL, 2))[:n_valid]
    cells = [
        H3Cell(index=idx, resolution=9, properties={"value": float(i + 1)})
        for i, idx in enumerate(valid_indices)
    ]
    # Malformed index: H3Cell.__post_init__ logs an init error but survives,
    # and h3.grid_disk raises ValueError for it during neighborhood lookup.
    cells.append(
        H3Cell(index=INVALID_CELL, resolution=9, properties={"value": 10.0})
    )
    return H3Grid(cells=cells)


def test_local_morans_fallback_logs_warning(caplog: pytest.LogCaptureFixture) -> None:
    """A grid_disk failure in Local Moran's I warns and degrades, not silently."""
    analyzer = H3SpatialAnalyzer(_grid_with_invalid_cell())
    with caplog.at_level(logging.WARNING):
        result = analyzer.detect_hotspots("value", method="local_morans")
    assert result["method"] == "Local Morans I"
    assert result["total_cells_analyzed"] == 6
    fallback_records = [
        r for r in caplog.records if f"grid_disk failed for {INVALID_CELL}" in r.message
    ]
    assert fallback_records, "expected a warning for the invalid cell"
    assert all(r.levelno == logging.WARNING for r in fallback_records)
    assert any("Local Moran's I" in r.message for r in fallback_records)


def test_getis_ord_fallback_logs_warning(caplog: pytest.LogCaptureFixture) -> None:
    """A grid_disk failure in Getis-Ord Gi* warns and falls back to self-only."""
    analyzer = H3SpatialAnalyzer(_grid_with_invalid_cell())
    with caplog.at_level(logging.WARNING):
        result = analyzer.detect_hotspots("value", method="getis_ord")
    assert result["method"] == "Getis-Ord Gi*"
    fallback_records = [
        r for r in caplog.records if f"grid_disk failed for {INVALID_CELL}" in r.message
    ]
    assert fallback_records, "expected a warning for the invalid cell"
    assert any(
        "self-only neighborhood in Getis-Ord Gi*" in r.message
        for r in fallback_records
    )


def test_spatial_lag_fallback_logs_warning(caplog: pytest.LogCaptureFixture) -> None:
    """A grid_disk failure in the local gradient warns that results may degrade."""
    analyzer = H3DensityAnalyzer(_grid_with_invalid_cell())
    with caplog.at_level(logging.WARNING):
        analyzer.analyze_density_patterns("value")
    fallback_records = [
        r for r in caplog.records if f"grid_disk failed for {INVALID_CELL}" in r.message
    ]
    assert fallback_records, "expected a warning for the invalid cell"
    assert any(
        "spatial lag (local gradient)" in r.message
        and "results may be degraded" in r.message
        for r in fallback_records
    )


def test_backend_cluster_fallback_logs_warning(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """find_clusters warns when grid_disk fails and treats the cell as noise."""
    backend = H3Backend()
    valid_indices = sorted(h3.grid_disk(SEED_CELL, 1))[:3]
    cells = [INVALID_CELL] + list(valid_indices)
    values = [1.0] + [float(i) for i in range(len(valid_indices))]
    with caplog.at_level(logging.WARNING):
        result = backend.find_clusters(cells, values, min_cluster_size=3)
    fallback_records = [
        r
        for r in caplog.records
        if f"grid_disk failed for cell {INVALID_CELL}" in r.message
    ]
    assert fallback_records, "expected a warning for the invalid cell"
    assert any("cluster expansion may degrade" in r.message for r in fallback_records)
    clustered_cells = {c for cluster in result["clusters"] for c in cluster["cells"]}
    assert INVALID_CELL not in clustered_cells
    assert clustered_cells == set(valid_indices)


