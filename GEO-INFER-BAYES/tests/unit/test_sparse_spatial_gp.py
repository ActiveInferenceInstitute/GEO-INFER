"""Tests for inducing-point variational spatial Gaussian processes."""

import numpy as np
import pytest
from numpy.testing import assert_allclose

from geo_infer_bayes import SparseSpatialGP as PublicSparseSpatialGP
from geo_infer_bayes.models import SparseSpatialGP


def spatial_signal(count: int = 120) -> tuple[np.ndarray, np.ndarray]:
    """Return a deterministic smooth one-dimensional spatial signal."""
    X = np.linspace(-2.0, 2.0, count)[:, None]
    y = np.sin(1.5 * X[:, 0]) + 0.15 * np.cos(4.0 * X[:, 0])
    return X, y


def test_sparse_gp_is_public_and_preserves_explicit_inducing_locations() -> None:
    X, y = spatial_signal()
    locations = X[::12]
    model = SparseSpatialGP(
        inducing_points=locations,
        kernel="rbf",
        lengthscale=0.6,
        noise=0.05,
        optimize_hyperparameters=False,
    ).fit(X, y)

    assert PublicSparseSpatialGP is SparseSpatialGP
    assert model.name == "SparseSpatialGP"
    assert_allclose(model.inducing_points_, locations)
    assert model.n_inducing_ == len(locations)


def test_automatic_inducing_selection_is_deterministic_and_caps_at_n() -> None:
    X, y = spatial_signal(18)
    first = SparseSpatialGP(n_inducing=7, optimize_hyperparameters=False).fit(X, y)
    second = SparseSpatialGP(n_inducing=7, optimize_hyperparameters=False).fit(X, y)
    saturated = SparseSpatialGP(n_inducing=40, optimize_hyperparameters=False).fit(
        X, y
    )

    assert_allclose(first.inducing_points_, second.inducing_points_)
    assert first.inducing_points_.shape == (7, 1)
    assert_allclose(saturated.inducing_points_, X)


def test_variational_posterior_is_finite_symmetric_and_positive_semidefinite() -> None:
    X, y = spatial_signal()
    model = SparseSpatialGP(
        n_inducing=14,
        kernel="matern",
        degree=1.5,
        noise=0.08,
        optimize_hyperparameters=False,
    ).fit(X, y)

    assert model.variational_mean_.shape == (14,)
    assert model.variational_covariance_.shape == (14, 14)
    assert np.all(np.isfinite(model.variational_mean_))
    assert_allclose(
        model.variational_covariance_, model.variational_covariance_.T, atol=1e-10
    )
    assert np.linalg.eigvalsh(model.variational_covariance_).min() >= -1e-10


def test_elbo_optimization_does_not_degrade_the_initial_bound() -> None:
    X, y = spatial_signal()
    model = SparseSpatialGP(
        n_inducing=16,
        kernel="rbf",
        lengthscale=0.08,
        variance=0.2,
        noise=0.8,
        max_iter=12,
    ).fit(X, y)

    assert model.optimization_result_ is not None
    assert np.isfinite(model.initial_elbo_)
    assert model.elbo_ >= model.initial_elbo_ - 1e-8
    assert model.elbo_history_ == [model.initial_elbo_, model.elbo_]
    assert model.compute_elbo() == pytest.approx(model.elbo_)


def test_sparse_prediction_returns_accurate_finite_latent_uncertainty() -> None:
    X, y = spatial_signal()
    model = SparseSpatialGP(
        n_inducing=20,
        kernel="rbf",
        lengthscale=0.5,
        variance=1.0,
        noise=0.03,
        optimize_hyperparameters=False,
    ).fit(X, y)

    mean, std = model.predict(X, return_std=True)

    assert mean.shape == y.shape
    assert std.shape == y.shape
    assert np.all(np.isfinite(mean))
    assert np.all(std > 0.0)
    assert np.sqrt(np.mean((mean - y) ** 2)) < 0.12


def test_large_fit_never_builds_a_dense_training_covariance() -> None:
    X, y = spatial_signal(10_001)
    model = SparseSpatialGP(
        n_inducing=10,
        kernel="rbf",
        lengthscale=0.4,
        noise=0.05,
        batch_size=512,
        optimize_hyperparameters=False,
    )
    kernel = model.kernel_fn
    observed_shapes: list[tuple[int, int]] = []

    def recording_kernel(left: np.ndarray, right: np.ndarray) -> np.ndarray:
        observed_shapes.append((len(left), len(right)))
        return kernel(left, right)

    model.kernel_fn = recording_kernel
    model.fit(X, y)

    assert model.inducing_points_.shape == (10, 1)
    assert (len(X), len(X)) not in observed_shapes
    assert max(left * right for left, right in observed_shapes) <= 5120


def test_sparse_posterior_predictive_replays_from_a_seed() -> None:
    X, y = spatial_signal(60)
    model = SparseSpatialGP(
        n_inducing=10,
        noise=0.05,
        optimize_hyperparameters=False,
    ).fit(X, y)

    first = model.posterior_predictive(X=X[:6], samples=4, random_seed=9)
    second = model.posterior_predictive(X=X[:6], samples=4, random_seed=9)

    assert first.shape == (4, 6)
    assert_allclose(first, second)


def test_sparse_gp_rejects_invalid_inputs_and_unfitted_prediction() -> None:
    with pytest.raises(ValueError, match="greater than zero"):
        SparseSpatialGP(n_inducing=0)
    with pytest.raises(ValueError, match="same number"):
        SparseSpatialGP(optimize_hyperparameters=False).fit(
            np.ones((3, 2)), np.ones(2)
        )
    with pytest.raises(ValueError, match="feature dimension"):
        SparseSpatialGP(
            inducing_points=np.ones((2, 3)), optimize_hyperparameters=False
        ).fit(np.ones((4, 2)), np.ones(4))
    with pytest.raises(ValueError, match="not been fitted"):
        SparseSpatialGP().predict(np.ones((2, 1)))
