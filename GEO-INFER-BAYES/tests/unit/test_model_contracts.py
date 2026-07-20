"""Regression tests for data-dependent Bayesian model contracts."""

from types import SimpleNamespace

import numpy as np
import pytest

from geo_infer_bayes.models import (
    BayesianNetwork,
    BayesianTimeSeriesModel,
    DirichletProcessMixture,
    DynamicSpatialModel,
    SpatialCausalModel,
    SpatialClusteringModel,
)
from geo_infer_bayes.models.spatial_gp import SpatialGP


def posterior(**samples):
    """Build a PosteriorAnalysis-compatible object from real numeric draws."""
    return SimpleNamespace(
        samples={key: np.asarray(value) for key, value in samples.items()}
    )


@pytest.mark.parametrize(
    ("model", "data", "theta", "X_new", "draws"),
    [
        (
            BayesianTimeSeriesModel(),
            {"observations": np.array([1.0, 1.5, 2.0]), "time": np.arange(3)},
            {"trend": 0.5, "seasonal": 0.2, "noise": 0.1},
            np.arange(4),
            {"trend": [0.4, 0.6], "seasonal": [0.1, 0.3], "noise": [0.1, 0.2]},
        ),
        (
            DynamicSpatialModel(),
            {
                "observations": np.array([1.0, 2.0, 3.0]),
                "X": np.array([[1, 0], [2, 1], [3, 2]]),
            },
            {"spatial_trend": 0.5, "temporal_trend": 0.2, "noise": 0.1},
            np.array([[1, 0], [2, 1]]),
            {
                "spatial_trend": [0.4, 0.6],
                "temporal_trend": [0.1, 0.3],
                "noise": [0.1, 0.2],
            },
        ),
        (
            BayesianNetwork(),
            {
                "observations": np.array([1.0, 2.0, 3.0]),
                "X": np.array([[1, 0], [2, 1], [3, 2]]),
            },
            {"edge_weights": [0.5, 0.2], "node_biases": [0.1]},
            np.array([[1, 0], [2, 1]]),
            {"edge_weights": [0.4, 0.6], "node_biases": [0.1, 0.2]},
        ),
        (
            SpatialCausalModel(),
            {
                "observations": np.array([1.0, 2.0, 3.0]),
                "X": np.array([[1, 0], [2, 1], [3, 2]]),
            },
            {"treatment_effect": 0.5, "spatial_confounding": 0.2},
            np.array([[1, 0], [2, 1]]),
            {"treatment_effect": [0.4, 0.6], "spatial_confounding": [0.1, 0.3]},
        ),
    ],
)
def test_models_compute_finite_data_dependent_contracts(
    model, data, theta, X_new, draws
):
    """Likelihood, prior, prediction, and predictive sampling are implemented."""
    assert np.isfinite(model.log_likelihood(theta, data))
    assert np.isfinite(model.log_prior(theta))
    model_posterior = posterior(**draws)
    prediction, uncertainty = model.predict(X_new, model_posterior, return_std=True)
    assert prediction.shape == (len(X_new),)
    assert uncertainty.shape == prediction.shape
    assert np.all(np.isfinite(prediction))
    assert np.all(uncertainty > 0)
    predictive = model.posterior_predictive(model_posterior, X_new, samples=3)
    assert predictive.shape == (3, len(X_new))
    assert np.all(np.isfinite(predictive))


def test_clustering_models_use_observed_signal():
    """Clustering predictions are derived from input values, not constants."""
    X = np.array([[1.0], [2.0], [10.0], [11.0]])
    for model in (
        SpatialClusteringModel(n_clusters=2),
        DirichletProcessMixture(max_clusters=2),
    ):
        assert (
            np.isfinite(
                model.log_likelihood(
                    {"cluster_means": [2.0, 10.0], "cluster_variances": [1.0, 1.0]}, X
                )
            )
            if isinstance(model, SpatialClusteringModel)
            else np.isfinite(model.log_likelihood({}, {"observations": X[:, 0]}))
        )
        prediction = model.predict(X)
        assert prediction.shape == (4,)
        assert prediction[0] != prediction[-1]


def test_spatial_gp_rejects_posterior_prediction_without_training_data():
    """A GP cannot silently return fabricated predictions before fitting."""
    model = SpatialGP()
    draws = posterior(lengthscale=[1.0], variance=[1.0], noise=[0.1])
    with pytest.raises(ValueError, match="fitted"):
        model.predict(np.array([[0.0, 0.0]]), draws)
