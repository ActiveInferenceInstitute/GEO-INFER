"""Tests for explicit random-seed threading in BAYES.

Two properties are checked for every stochastic entry point:

* Replay -- equal seeds give equal output, distinct seeds give distinct output,
  and a caller-owned ``Generator`` is threaded through rather than ignored.
* Isolation -- the process-wide ``numpy.random`` stream is never read or
  advanced, so a caller's global state cannot silently change a posterior and
  an inference run cannot perturb a caller's own stream.
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


@pytest.fixture
def observations() -> dict:
    return {"observations": np.array([0.5, -0.3, 1.1])}


@pytest.fixture
def grid() -> tuple:
    coords = np.arange(100).reshape(50, 2).astype(float)
    values = np.arange(50).astype(float)
    return coords, values


def test_model_comparison_seed_replay(observations: dict) -> None:
    """compare_models with a seed replays identically when prior-drawing."""
    a = ModelComparison([_dummy_model()]).compare_models(
        observations, method="loo", random_seed=7
    )
    b = ModelComparison([_dummy_model()]).compare_models(
        observations, method="loo", random_seed=7
    )
    assert a["dummy"]["elpd_loo"] == b["dummy"]["elpd_loo"] <= 0.0


def test_model_comparison_different_seeds_differ(observations: dict) -> None:
    a = ModelComparison([_dummy_model()]).compare_models(
        observations, method="loo", random_seed=1
    )
    b = ModelComparison([_dummy_model()]).compare_models(
        observations, method="loo", random_seed=2
    )
    assert a["dummy"]["elpd_loo"] != b["dummy"]["elpd_loo"]


def test_model_comparison_accepts_a_generator(observations: dict) -> None:
    """A caller-owned Generator is used instead of being coerced to a seed."""
    a = ModelComparison([_dummy_model()]).compare_models(
        observations, method="loo", random_seed=np.random.default_rng(13)
    )
    b = ModelComparison([_dummy_model()]).compare_models(
        observations, method="loo", random_seed=np.random.default_rng(13)
    )
    assert a["dummy"]["elpd_loo"] == b["dummy"]["elpd_loo"]


def test_model_comparison_leaves_global_stream_untouched(observations: dict) -> None:
    np.random.seed(5)
    expected = np.random.random()

    np.random.seed(5)
    ModelComparison([_dummy_model()]).compare_models(observations, method="loo")
    assert np.random.random() == expected


def test_sample_spatial_data_seed_replay(grid: tuple) -> None:
    coords, values = grid
    a = sample_spatial_data(coords, values, n_samples=10, random_seed=3)
    b = sample_spatial_data(coords, values, n_samples=10, random_seed=3)
    assert np.array_equal(a[0], b[0])
    assert np.array_equal(a[1], b[1])
    assert a[0].shape == (10, 2)


def test_sample_spatial_data_different_seeds_differ(grid: tuple) -> None:
    coords, values = grid
    a = sample_spatial_data(coords, values, n_samples=10, random_seed=3)
    b = sample_spatial_data(coords, values, n_samples=10, random_seed=4)
    assert not np.array_equal(a[0], b[0])


def test_sample_spatial_data_stratified_replay() -> None:
    coords = np.arange(200).reshape(100, 2).astype(float)
    values = np.arange(100).astype(float)
    a = sample_spatial_data(
        coords, values, n_samples=20, method="stratified", random_seed=8
    )
    b = sample_spatial_data(
        coords, values, n_samples=20, method="stratified", random_seed=8
    )
    assert np.array_equal(a[0], b[0])


def test_sample_spatial_data_accepts_a_generator(grid: tuple) -> None:
    coords, values = grid
    a = sample_spatial_data(
        coords, values, n_samples=10, random_seed=np.random.default_rng(2)
    )
    b = sample_spatial_data(
        coords, values, n_samples=10, random_seed=np.random.default_rng(2)
    )
    assert np.array_equal(a[0], b[0])


def test_sample_spatial_data_leaves_global_stream_untouched(grid: tuple) -> None:
    """Sampling draws from its own generator, not the numpy.random singleton."""
    coords, values = grid
    np.random.seed(5)
    expected = np.random.random()

    np.random.seed(5)
    sample_spatial_data(coords, values, n_samples=10)
    assert np.random.random() == expected
