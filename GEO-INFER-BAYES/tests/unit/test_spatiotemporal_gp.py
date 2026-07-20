"""Regression tests for the spatio-temporal Gaussian-process contract."""

from types import SimpleNamespace

import numpy as np
import pytest

from geo_infer_bayes.models.spatiotemporal_gp import (
    SpatioTemporalConfig,
    SpatioTemporalGP,
)


@pytest.fixture
def fitted_model() -> tuple[SpatioTemporalGP, np.ndarray, np.ndarray, np.ndarray]:
    spatial = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
    temporal = np.arange(4.0)
    observations = np.array([1.0, 2.0, 1.5, 2.5])
    model = SpatioTemporalGP(
        SpatioTemporalConfig(observation_noise=0.05, random_seed=42)
    )
    model.fit(spatial, temporal, observations)
    return model, spatial, temporal, observations


def posterior_draws() -> SimpleNamespace:
    return SimpleNamespace(
        samples={
            "spatial_lengthscale": np.array([0.8, 1.0]),
            "spatial_variance": np.array([0.9, 1.1]),
            "temporal_lengthscale": np.array([0.8, 1.0]),
            "temporal_variance": np.array([0.1, 0.2]),
            "noise": np.array([0.05, 0.08]),
        }
    )


def test_canonical_and_legacy_prediction_inputs_match(fitted_model) -> None:
    model, spatial, temporal, _ = fitted_model
    X = np.column_stack((spatial, temporal))

    canonical = model.predict(X)
    legacy = model.predict(spatial, temporal)

    assert canonical.shape == (4,)
    np.testing.assert_allclose(canonical, legacy)


def test_posterior_prediction_and_predictive_sampling_are_finite(fitted_model) -> None:
    model, spatial, temporal, _ = fitted_model
    X = np.column_stack((spatial, temporal))
    posterior = posterior_draws()

    mean, spread = model.predict(X, posterior, return_std=True)
    predictive = model.posterior_predictive(posterior, X, samples=2)

    assert mean.shape == (4,)
    assert spread.shape == (4,)
    assert predictive.shape == (2, 4)
    assert np.all(np.isfinite(mean))
    assert np.all(np.isfinite(spread))
    assert np.all(np.isfinite(predictive))


def test_log_likelihood_does_not_mutate_model_parameters(fitted_model) -> None:
    model, spatial, temporal, observations = fitted_model
    theta = {
        "spatial_lengthscale": 0.8,
        "spatial_variance": 0.9,
        "temporal_lengthscale": 1.0,
        "temporal_variance": 0.2,
        "noise": 0.05,
    }
    original_lengthscale = model.spatial_gp.lengthscale
    value = model.log_likelihood(
        theta,
        {
            "spatial_coords": spatial,
            "temporal_coords": temporal,
            "observations": observations,
        },
    )

    assert np.isfinite(value)
    assert model.spatial_gp.lengthscale == original_lengthscale


def test_prediction_shape_and_fit_validation_are_explicit() -> None:
    model = SpatioTemporalGP()
    with pytest.raises(ValueError, match="shape"):
        model.predict(np.zeros((2, 2)))
    with pytest.raises(ValueError, match="fitted"):
        model.predict(np.zeros((1, 3)))
