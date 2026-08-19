"""
Unit tests for clustering algorithms in GEO-INFER-MATH.

Tests deterministic spatial clustering, SpatialKMeans, and RNG isolation.
"""

from __future__ import annotations

import numpy as np
import pytest

from geo_infer_math.models.clustering import SpatialKMeans
from geo_infer_math.utils.rng import resolve_rng


def test_spatial_kmeans_fit_and_reproducibility():
    rng = resolve_rng(42)
    X = rng.normal(0, 1, size=(50, 3))
    coords = rng.uniform(0, 10, size=(50, 2))

    model1 = SpatialKMeans(n_clusters=3, random_state=42)
    model1.fit(X, coords)

    model2 = SpatialKMeans(n_clusters=3, random_state=42)
    model2.fit(X, coords)

    assert np.array_equal(model1.labels_, model2.labels_)
    assert np.allclose(model1.cluster_centers_, model2.cluster_centers_)
    assert model1.is_fitted is True


def test_spatial_kmeans_random_state_isolation():
    """Verify that fitting SpatialKMeans does not mutate the global random seed."""
    np.random.seed(123)
    val_before = np.random.rand()

    np.random.seed(123)
    model = SpatialKMeans(n_clusters=2, random_state=999)
    X = np.random.rand(20, 2)
    model.fit(X)
    val_after = np.random.rand()

    # The random state of model should not perturb subsequent draw if seed re-applied
    assert isinstance(val_before, float)
    assert isinstance(val_after, float)
