"""Tests for deterministic random-seed threading in BAYES.

Verifies the REPRO-01 migration: public BAYES helpers accept ``random_seed``
and produce identical output across calls for the same seed, while the default
(``random_seed=None``) continues to use the legacy global ``np.random`` state.
"""

from __future__ import annotations

import numpy as np
import pytest

from geo_infer_bayes.core.model_comparison import ModelComparison
from geo_infer_bayes.utils.data_processing import sample_spatial_data


def _dummy_model() -> object:
    """A minimal model with a prior-drawable parameter space."""
    class _Dummy:
        name = "dummy"

        parameters = {
            "alpha": {"prior": "normal", "hyperparams": {"mu": 0.0, "sigma": 1.0}},
        }

        def log_likelihood(self, theta, obs):  # pragma: no cover - minimal helper
            return -0.5 * float((obs[0] - theta["alpha"]) ** 2)

    return _Dummy()


def test_model_comparison_seed_replay() -> None:
    """compare_models with a seed replays identically when prior-drawing."""
    data = {"observations": np.array([0.5, -0.3, 1.1])}
    a = ModelComparison([_dummy_model()]).compare_models(data, method="loo", random_seed=7)
    b = ModelComparison([_dummy_model()]).compare_models(data, method="loo", random_seed=7)
    assert a["dummy"]["elpd_loo"] == b["dummy"]["elpd_loo"] <= 0.0


def test_model_comparison_different_seeds_differ() -> None:
    data = {"observations": np.array([0.5, -0.3, 1.1])}
    a = ModelComparison([_dummy_model()]).compare_models(data, method="loo", random_seed=1)
    b = ModelComparison([_dummy_model()]).compare_models(data, method="loo", random_seed=2)
    assert a["dummy"]["elpd_loo"] != b["dummy"]["elpd_loo"]


def test_sample_spatial_data_seed_replay() -> None:
    coords = np.arange(100).reshape(50, 2).astype(float)
    values = np.arange(50).astype(float)
    a = sample_spatial_data(coords, values, n_samples=10, random_seed=3)
    b = sample_spatial_data(coords, values, n_samples=10, random_seed=3)
    assert np.array_equal(a[0], b[0])
    assert np.array_equal(a[1], b[1])
    assert a[0].shape == (10, 2)


def test_sample_spatial_data_stratified_replay() -> None:
    coords = np.arange(200).reshape(100, 2).astype(float)
    values = np.arange(100).astype(float)
    a = sample_spatial_data(coords, values, n_samples=20, method="stratified", random_seed=8)
    b = sample_spatial_data(coords, values, n_samples=20, method="stratified", random_seed=8)
    assert np.array_equal(a[0], b[0])


def test_sample_spatial_data_default_uses_global_state() -> None:
    coords = np.arange(100).reshape(50, 2).astype(float)
    values = np.arange(50).astype(float)
    np.random.seed(5)
    a = sample_spatial_data(coords, values, n_samples=10)
    np.random.seed(5)
    b = sample_spatial_data(coords, values, n_samples=10)
    assert np.array_equal(a[0], b[0])
