"""Tests for deterministic random-seed threading in SPM helpers.

Verifies the REPRO-01 migration: public SPM helpers accept ``random_seed`` and
produce identical outputs across separate calls when given the same seed, while
the default (``random_seed=None``) continues to use the legacy global
``np.random`` state so existing callers are unaffected.
"""

from __future__ import annotations

import numpy as np
import pytest

from geo_infer_spm.utils.helpers import (
    compute_power_analysis,
    create_spatial_basis_functions,
    generate_coordinates,
    generate_synthetic_data,
)


def test_generate_coordinates_seed_replay() -> None:
    a = generate_coordinates("random", n_points=50, random_seed=7)
    b = generate_coordinates("random", n_points=50, random_seed=7)
    assert np.array_equal(a, b)
    assert a.shape == (50, 2)


def test_generate_coordinates_different_seeds_differ() -> None:
    a = generate_coordinates("random", n_points=50, random_seed=1)
    b = generate_coordinates("random", n_points=50, random_seed=2)
    assert not np.array_equal(a, b)


def test_generate_coordinates_clustered_seed_replay() -> None:
    a = generate_coordinates("clustered", n_points=30, random_seed=3)
    b = generate_coordinates("clustered", n_points=30, random_seed=3)
    assert np.array_equal(a, b)


def test_generate_synthetic_data_seed_replay() -> None:
    coords = generate_coordinates("regular", n_points=25)
    a = generate_synthetic_data(coords, random_seed=11)
    b = generate_synthetic_data(coords, random_seed=11)
    assert a.data is not None and b.data is not None
    assert np.array_equal(a.data, b.data)
    assert a.covariates is not None and b.covariates is not None
    assert np.array_equal(a.covariates["elevation"], b.covariates["elevation"])


def test_create_spatial_basis_functions_seed_replay() -> None:
    coords = generate_coordinates("regular", n_points=20)
    a = create_spatial_basis_functions(coords, n_basis=5, random_seed=42)
    b = create_spatial_basis_functions(coords, n_basis=5, random_seed=42)
    assert np.array_equal(a, b)


def test_create_spatial_basis_functions_deterministic_seed() -> None:
    """Explicit seed provides deterministic results."""
    coords = generate_coordinates("regular", n_points=20, random_seed=42)
    a = create_spatial_basis_functions(coords, n_basis=5, random_seed=42)
    b = create_spatial_basis_functions(coords, n_basis=5, random_seed=42)
    assert np.array_equal(a, b)


def test_compute_power_analysis_seed_replay() -> None:
    a = compute_power_analysis(0.5, n_points=30, n_simulations=50, random_seed=9)
    b = compute_power_analysis(0.5, n_points=30, n_simulations=50, random_seed=9)
    assert a["power"] == b["power"]
    assert a["power"] is not None


def test_compute_power_analysis_default_uses_global_state() -> None:
    """Default path draws from global np.random state (legacy behaviour)."""
    np.random.seed(5)
    a = compute_power_analysis(0.5, n_points=30, n_simulations=50)
    np.random.seed(5)
    b = compute_power_analysis(0.5, n_points=30, n_simulations=50)
    assert a["power"] == b["power"]
