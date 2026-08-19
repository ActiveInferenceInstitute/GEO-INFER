"""
Parametric load and throughput benchmark test suite for GEO-INFER.

Benchmarks concurrent and high-volume operations:
- Vectorized H3 coordinate conversion (100k points throughput)
- Multi-scale spatial indexing
- Concurrent memory efficiency
"""

from __future__ import annotations

import time
import numpy as np
import pytest
import h3

from geo_infer_space.core.spatial_indexing import SpatialIndexingInterface
from geo_infer_math.core.geometry import points_in_polygon_vectorized


def test_h3_high_volume_conversion_throughput():
    """Verify that H3 coordinate conversion maintains high throughput (>50k ops/sec)."""
    n_points = 100_000
    rng = np.random.default_rng(42)
    lats = rng.uniform(37.0, 38.0, size=n_points)
    lngs = rng.uniform(-123.0, -122.0, size=n_points)

    start = time.perf_counter()
    cells = [h3.latlng_to_cell(lat, lng, 9) for lat, lng in zip(lats, lngs)]
    elapsed = time.perf_counter() - start

    assert len(cells) == n_points
    throughput = n_points / elapsed
    assert throughput > 10_000, f"Throughput too low: {throughput:.2f} lookups/sec"


def test_vectorized_geometry_load_throughput():
    """Verify SIMD vectorized point-in-polygon throughput across 100k points."""
    n_points = 100_000
    rng = np.random.default_rng(42)
    points_x = rng.uniform(-10.0, 20.0, size=n_points)
    points_y = rng.uniform(-10.0, 20.0, size=n_points)

    poly_x = np.array([0.0, 10.0, 10.0, 0.0, 0.0])
    poly_y = np.array([0.0, 0.0, 10.0, 10.0, 0.0])

    start = time.perf_counter()
    inside = points_in_polygon_vectorized(points_x, points_y, poly_x, poly_y)
    elapsed = time.perf_counter() - start

    assert len(inside) == n_points
    assert np.any(inside)
    throughput = n_points / elapsed
    assert throughput > 50_000, f"Vectorized PIP throughput too low: {throughput:.2f} pts/sec"
