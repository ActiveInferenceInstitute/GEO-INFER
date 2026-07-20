"""Regression tests for ABC and SMC sampler contracts."""

import numpy as np

from geo_infer_bayes.core.abc import ApproximateBayesianComputation
from geo_infer_bayes.core.smc import SequentialMonteCarlo
from geo_infer_bayes.models.bayesian_network import BayesianNetwork
from geo_infer_bayes.models.bayesian_timeseries import BayesianTimeSeriesModel


def test_abc_mahalanobis_distance_supports_vector_observations() -> None:
    sampler = ApproximateBayesianComputation(
        BayesianTimeSeriesModel(), distance_metric="mahalanobis", random_seed=7
    )

    value = sampler._compute_distance(
        np.array([1.0, 2.0, 3.0]), np.array([1.1, 1.9, 3.2])
    )

    assert np.isfinite(value)
    assert value >= 0


def test_abc_sampling_is_reproducible_and_does_not_touch_global_rng() -> None:
    model = BayesianTimeSeriesModel()
    prior = {
        "trend": np.arange(10.0),
        "seasonal": np.arange(10.0),
        "noise": np.ones(10),
    }
    observed = np.array([0.0])
    def simulator(theta):
        return np.array([theta["trend"]])

    np.random.seed(123)
    state = np.random.get_state()
    expected_next = np.random.random()
    np.random.set_state(state)
    first = ApproximateBayesianComputation(
        model, tolerance=10.0, n_samples=5, random_seed=11
    ).run(observed, simulator=simulator, prior_samples=prior, progress_bar=False)
    actual_next = np.random.random()
    second = ApproximateBayesianComputation(
        model, tolerance=10.0, n_samples=5, random_seed=11
    ).run(observed, simulator=simulator, prior_samples=prior, progress_bar=False)

    np.testing.assert_allclose(actual_next, expected_next)
    for parameter in prior:
        np.testing.assert_allclose(first[parameter], second[parameter])


def test_smc_preserves_log_normal_support_and_parameter_order() -> None:
    model = BayesianNetwork()
    sampler = SequentialMonteCarlo(model, n_particles=8, random_seed=5)
    data = {
        "X": np.array([[1.0, 0.0], [2.0, 1.0], [3.0, 2.0]]),
        "observations": np.array([1.0, 2.0, 3.0]),
    }
    samples = sampler.run(data, n_steps=2, progress_bar=False)

    assert list(samples) == ["edge_weights", "node_biases"]
    assert np.all(np.isfinite(samples["edge_weights"]))
    assert np.all(np.isfinite(samples["node_biases"]))
