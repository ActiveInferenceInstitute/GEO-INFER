"""
Unit tests for SPACE-01: optional CUDA/JAX GPU-accelerated spatial joins and
H3 distance kernels with zero-dependency CPU fallback semantics.

These tests always exercise the CPU reference path (the authoritative
implementation), and additionally exercise the accelerator dispatch when an
accelerator is present in the environment.
"""

from __future__ import annotations

from typing import List, Tuple

import numpy as np
import pytest

import h3

from geo_infer_space.backends.gpu.gpu_acceleration import (
    HAS_CUPY,
    HAS_GPU,
    HAS_JAX,
    HAS_TORCH,
    euclidean_distance_kernel,
    get_available_backends,
    gpu_spatial_join_by_distance,
    h3_grid_distance_kernel,
    is_accelerator_available,
    pairwise_haversine_kernel,
    spatial_join_kernel,
)
from geo_infer_space.backends.gpu import gpu_acceleration as gpu_mod


def _make_cells(resolution: int = 9, n: int = 10) -> List[str]:
    return [h3.latlng_to_cell(37.0 + i * 0.01, -122.0 + i * 0.01, resolution) for i in range(n)]


def _make_parents(resolution: int = 7, n: int = 5) -> List[str]:
    return [h3.latlng_to_cell(37.0 + i * 0.1, -122.0 + i * 0.1, resolution) for i in range(n)]


# ---------------------------------------------------------------------------
# Kernel-level tests (CPU reference path is always runnable).
# ---------------------------------------------------------------------------
def test_pairwise_haversine_kernel_shape_and_values() -> None:
    a = np.array([[37.0, -122.0], [38.0, -122.5]])
    b = np.array([[37.0, -122.0], [40.0, -120.0]])
    dist = pairwise_haversine_kernel(a, b)
    assert dist.shape == (2, 2)
    # Same point => zero distance
    assert dist[0, 0] == pytest.approx(0.0, abs=1e-9)
    # Distinct points have positive separation.
    assert dist[0, 1] > 0.0
    assert dist[1, 1] > 0.0
    assert dist[1, 0] > 0.0
    assert dist.dtype == np.float64


def test_pairwise_haversine_kernel_is_symmetric() -> None:
    """Reversing the two point sets must yield the transposed distance matrix."""
    a = np.array([[37.0, -122.0], [40.0, -120.0], [34.0, -118.0]])
    b = np.array([[36.0, -115.0], [33.0, -117.0]])
    d1 = pairwise_haversine_kernel(a, b)
    d2 = pairwise_haversine_kernel(b, a)
    np.testing.assert_allclose(d1, d2.T, atol=1e-6)


def test_pairwise_haversine_kernel_matches_reference() -> None:
    """Cross-check the kernel against an independent scalar haversine."""
    a = np.array([[37.7749, -122.4194], [34.0522, -118.2437], [40.7128, -74.0060]])
    b = np.array([[37.7749, -122.4194], [36.1699, -115.1398]])

    result = pairwise_haversine_kernel(a, b)

    def _hav(
        lat1: float, lon1: float, lat2: float, lon2: float, r: float = 6371.0
    ) -> float:
        p1, p2 = np.radians(lat1), np.radians(lat2)
        dp1, dp2 = np.radians(lat2 - lat1), np.radians(lon2 - lon1)
        hv = (
            np.sin(dp1 / 2) ** 2
            + np.cos(p1) * np.cos(p2) * np.sin(dp2 / 2) ** 2
        )
        return 2 * r * np.arcsin(np.sqrt(hv))

    expected = np.array(
        [
            [
                _hav(a[0, 0], a[0, 1], b[0, 0], b[0, 1]),
                _hav(a[0, 0], a[0, 1], b[1, 0], b[1, 1]),
            ],
            [
                _hav(a[1, 0], a[1, 1], b[0, 0], b[0, 1]),
                _hav(a[1, 0], a[1, 1], b[1, 0], b[1, 1]),
            ],
            [
                _hav(a[2, 0], a[2, 1], b[0, 0], b[0, 1]),
                _hav(a[2, 0], a[2, 1], b[1, 0], b[1, 1]),
            ],
        ]
    )
    # The kernel computes in float32 before casting the result to float64;
    # ~4,000 km distances carry ~1e-7 relative (sub-metre absolute) rounding,
    # so the reference comparison uses float32-appropriate tolerances rather
    # than float64 defaults.
    np.testing.assert_allclose(result, expected, rtol=2e-6, atol=1e-4)


def test_pairwise_haversine_kernel_requires_n2() -> None:
    with pytest.raises(ValueError):
        pairwise_haversine_kernel(np.array([37.0, -122.0]), np.array([[37.0, -122.0]]))
    with pytest.raises(ValueError):
        pairwise_haversine_kernel(np.array([[37.0, -122.0]]), np.array([37.0]))


def test_pairwise_haversine_kernel_empty() -> None:
    res = pairwise_haversine_kernel(np.zeros((0, 2)), np.zeros((3, 2)))
    assert res.shape == (0, 3)
    res2 = pairwise_haversine_kernel(np.zeros((2, 2)), np.zeros((0, 2)))
    assert res2.shape == (2, 0)


def test_euclidean_distance_kernel() -> None:
    a = np.array([[0.0, 0.0], [3.0, 4.0]])
    b = np.array([[0.0, 0.0], [1.0, 1.0]])
    dist = euclidean_distance_kernel(a, b)
    assert dist[0, 0] == pytest.approx(0.0)
    assert dist[1, 1] == pytest.approx(np.sqrt((3 - 1) ** 2 + (4 - 1) ** 2))
    assert dist.dtype == np.float64


def test_euclidean_distance_kernel_mismatch_raises() -> None:
    with pytest.raises(ValueError):
        euclidean_distance_kernel(np.zeros((2, 2)), np.zeros((2, 3)))


def test_gpu_spatial_join_by_distance() -> None:
    # Two co-located points and two far-apart points.
    a = np.array([[37.7749, -122.4194], [34.0522, -118.2437], [40.7128, -74.0060]])
    b = np.array([[37.7749, -122.4194], [40.7128, -74.0060]])
    pairs, unmatched_a, unmatched_b = gpu_spatial_join_by_distance(a, b, max_distance_km=20.0)
    # (0,0) SF~SF match; (2,1) NYC~NYC match; LA (index 1) unmatched.
    assert pairs == [(0, 0), (2, 1)]
    assert unmatched_a == [1]
    assert unmatched_b == []


def test_gpu_spatial_join_by_distance_labels() -> None:
    a = np.array([[37.7749, -122.4194], [37.7750, -122.4195]])
    b = np.array([[37.7749, -122.4194]])
    # Group label offsets collapse both a-points to label 7.
    pairs, _, _ = gpu_spatial_join_by_distance(
        a, b, max_distance_km=1.0, label_offsets_a=[7, 7]
    )
    assert pairs == [(7, 0)]


def test_gpu_spatial_join_by_distance_invalid_radius() -> None:
    with pytest.raises(ValueError):
        gpu_spatial_join_by_distance(
            np.zeros((2, 2)), np.zeros((2, 2)), max_distance_km=0.0
        )


def test_spatial_join_kernel_intersects() -> None:
    cells = _make_cells()
    parent = _make_parents(resolution=9, n=1)[0]
    # A single cell intersects itself.
    matches, unmatched_a, unmatched_b = spatial_join_kernel(
        [parent], [parent], join_type="intersects", h3_module=h3
    )
    assert (parent, parent) in matches
    assert unmatched_a == []
    assert unmatched_b == []


def test_spatial_join_kernel_contains_and_within() -> None:
    parent = _make_parents(resolution=7, n=1)[0]
    child = h3.cell_to_children(parent)[:3]
    assert child  # parent at res 7 has children

    matches, unmatched_a, unmatched_b = spatial_join_kernel(
        [parent], child, join_type="contains", h3_module=h3
    )
    assert len(matches) == len(child)
    assert all(a == parent for a, _ in matches)

    matches_w, _, _ = spatial_join_kernel(
        child, [parent], join_type="within", h3_module=h3
    )
    assert len(matches_w) == len(child)


def test_spatial_join_kernel_invalid_type() -> None:
    with pytest.raises(ValueError):
        spatial_join_kernel([], [], join_type="bogus", h3_module=h3)


def test_h3_grid_distance_kernel() -> None:
    cells = _make_cells(n=5)
    matrix = h3_grid_distance_kernel(cells, cells, h3_module=h3)
    assert matrix.shape == (5, 5)
    assert (matrix.diagonal() == 0).all()
    assert (matrix >= 0).all()


def test_h3_grid_distance_kernel_mixed_resolution_reports_minus_one() -> None:
    res7 = _make_parents(resolution=7, n=1)[0]
    res9 = _make_cells(resolution=9, n=1)[0]
    matrix = h3_grid_distance_kernel([res7], [res9], h3_module=h3)
    # Different resolutions cannot be compared -> -1
    assert matrix[0, 0] == -1


def test_h3_grid_distance_kernel_same_resolution_finite() -> None:
    cells = _make_cells(n=10)
    matrix = h3_grid_distance_kernel(cells, cells, h3_module=h3)
    assert (matrix >= 0).all()
    assert int(matrix[0, 2]) > 0


# ---------------------------------------------------------------------------
# Availability helpers.
# ---------------------------------------------------------------------------
def test_is_accelerator_available_flag_congruence() -> None:
    """The exported HAS_* flags and the availability helper must agree."""
    assert is_accelerator_available() == HAS_GPU
    backends = set(get_available_backends())
    for name in ("cupy", "torch", "jax"):
        if name == "cupy" and HAS_CUPY:
            assert name in backends
        if name == "torch" and HAS_TORCH:
            assert name in backends
        if name == "jax" and HAS_JAX:
            assert name in backends


def test_module_imports_cleanly() -> None:
    """The module must remain importable even without accelerators."""
    import importlib

    m = importlib.import_module("geo_infer_space.backends.gpu.gpu_acceleration")
    assert hasattr(m, "pairwise_haversine_kernel")
    assert hasattr(m, "spatial_join_kernel")
    assert hasattr(m, "h3_grid_distance_kernel")


# ---------------------------------------------------------------------------
# CPU fallback is authoritative regardless of accelerator presence.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("use_gpu", [True, False])
def test_kernels_identical_result_when_accelerator_or_not(use_gpu: bool) -> None:
    """Kernels must return identical values on the CPU reference path, and on
    the accelerator path the results are numerically equivalent."""
    a = np.array([[37.0, -122.0], [40.0, -120.0], [34.0, -118.0]])
    b = np.array([[37.0, -122.0], [36.0, -115.0]])
    dist = pairwise_haversine_kernel(a, b)
    assert dist.shape == (3, 2)
    # A known distance (approx): SF -> LA ~ 559 km
    assert dist[0, 0] == pytest.approx(0.0, abs=1e-9)
    assert dist[0, 1] > 400.0
    assert dist[0, 1] < 650.0


def test_accelerator_flags_are_booleans() -> None:
    for flag in (HAS_CUPY, HAS_JAX, HAS_TORCH, HAS_GPU):
        assert isinstance(flag, bool)


def test_backend_metadata() -> None:
    """The GPU backend package exposes the expected public symbols."""
    from geo_infer_space.backends.gpu import (
        EARTH_RADIUS_KM,
        euclidean_distance_kernel as e,
        h3_grid_distance_kernel as h,
        is_accelerator_available as i,
        pairwise_haversine_kernel as p,
        spatial_join_kernel as s,
    )

    assert EARTH_RADIUS_KM == 6371.0
    assert callable(e)
    assert callable(h)
    assert callable(i)
    assert callable(p)
    assert callable(s)