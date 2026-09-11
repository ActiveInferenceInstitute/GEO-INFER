"""
Unit tests for the public API interfaces (Stan, TFP, PyMC).

Covers the surfaces that are usable without optional backends: Stan
model-code generation, the pure-NumPy/SciPy TFP fit-sample-predict round
trip, and PyMC model construction (skipped when pymc is not installed).
"""

import numpy as np
import pytest
from numpy.testing import assert_allclose

from geo_infer_bayes.api import StanInterface, TFPInterface

import pymc as pm


def _synthetic_gp_data(n: int = 15) -> tuple[np.ndarray, np.ndarray]:
    """One-dimensional GP training data with a mild observation noise."""
    rng = np.random.default_rng(7)
    X = np.linspace(0.0, 1.0, n).reshape(-1, 1)
    y = np.sin(2.0 * np.pi * X[:, 0]) + 0.01 * rng.normal(size=n)
    return X, y


class TestStanInterface:
    """Stan code generation requires no compiled Stan backend."""

    def test_create_spatial_gp_model_returns_generated_code(self):
        interface = StanInterface()
        X, y = _synthetic_gp_data()

        code = interface.create_spatial_gp_model(X, y)

        assert isinstance(code, str)
        for block in ("data {", "parameters {", "model {"):
            assert block in code

    def test_generated_code_declares_gp_data_block(self):
        interface = StanInterface()
        X, y = _synthetic_gp_data()

        code = interface.create_spatial_gp_model(X, y)

        assert "int<lower=1> N;" in code
        assert "int<lower=1> D;" in code
        assert "vector[N] y;" in code
        assert "matrix[N, D] X;" in code

    def test_generated_code_declares_positive_kernel_parameters(self):
        interface = StanInterface()
        X, y = _synthetic_gp_data()

        code = interface.create_spatial_gp_model(X, y)

        for name in ("lengthscale", "variance", "noise"):
            assert f"real<lower=0> {name};" in code

    def test_generated_code_encodes_gaussian_process_likelihood(self):
        interface = StanInterface()
        X, y = _synthetic_gp_data()

        code = interface.create_spatial_gp_model(X, y)

        assert "multi_normal" in code
        assert "exp(-0.5" in code
        assert "lengthscale * lengthscale" in code

    def test_sample_without_backend_raises_runtime_error(self):
        interface = StanInterface()

        with pytest.raises(RuntimeError, match="compiled Stan backend"):
            interface.sample(n_samples=10, n_warmup=5)


class TestTFPInterface:
    """TFPInterface runs on the documented permanent NumPy/SciPy backend."""

    def test_create_spatial_gp_model_returns_summary_with_fitted_state(self):
        interface = TFPInterface()
        X, y = _synthetic_gp_data()

        summary = interface.create_spatial_gp_model(
            X, y, lengthscale=0.3, variance=1.0, noise=0.01
        )

        assert isinstance(summary, str)
        assert f"n={len(X)}" in summary
        assert "d=1" in summary
        assert "lengthscale = 0.3000" in summary
        assert "log-marginal-likelihood" in summary

    def test_fit_sample_predict_round_trip(self):
        interface = TFPInterface()
        X, y = _synthetic_gp_data()

        interface.create_spatial_gp_model(
            X, y, lengthscale=0.3, variance=1.0, noise=0.01
        )
        traces = interface.sample(n_samples=60, n_warmup=40, seed=42)

        assert set(traces) == {"lengthscale", "variance", "noise"}
        for values in traces.values():
            assert values.shape == (60,)
            assert np.all(np.isfinite(values))
            assert np.all(values > 0)

        mean, std = interface.predict(X, return_std=True)

        assert mean.shape == (len(X),)
        assert std.shape == (len(X),)
        # The posterior mean interpolates the training observations up to
        # the observation noise.
        assert np.max(np.abs(mean - y)) < 0.05

        grid = np.linspace(0.0, 1.0, 41).reshape(-1, 1)
        grid_mean, grid_std = interface.predict(grid, return_std=True)

        assert np.all(np.isfinite(grid_mean))
        assert np.all(grid_std > 0)
        # Predictions stay close to the generating function away from the
        # domain edges.
        interior = (grid[:, 0] > 0.15) & (grid[:, 0] < 0.85)
        assert (
            np.max(np.abs(grid_mean[interior] - np.sin(2 * np.pi * grid[interior, 0])))
            < 0.2
        )

    def test_predict_returns_mean_only_when_std_not_requested(self):
        interface = TFPInterface()
        X, y = _synthetic_gp_data()
        interface.create_spatial_gp_model(X, y)

        mean = interface.predict(X, return_std=False)

        assert isinstance(mean, np.ndarray)
        assert mean.shape == (len(X),)

    def test_predict_accepts_one_dimensional_locations(self):
        interface = TFPInterface()
        X, y = _synthetic_gp_data()
        interface.create_spatial_gp_model(X, y)

        mean, std = interface.predict(np.array([0.25, 0.5, 0.75]))

        assert mean.shape == (3,)
        assert std.shape == (3,)

    def test_sample_is_reproducible_for_fixed_seed(self):
        interface = TFPInterface()
        X, y = _synthetic_gp_data()
        interface.create_spatial_gp_model(X, y, lengthscale=0.3)

        first = interface.sample(n_samples=20, n_warmup=20, seed=42)
        second = interface.sample(n_samples=20, n_warmup=20, seed=42)

        for key in first:
            assert_allclose(first[key], second[key])

    def test_sample_without_fit_returns_prior_samples(self):
        interface = TFPInterface()

        traces = interface.sample(n_samples=10)

        assert set(traces) == {"lengthscale", "variance", "noise"}
        for values in traces.values():
            assert values.shape == (10,)
            assert np.all(values > 0)

    def test_predict_before_fit_raises_runtime_error(self):
        interface = TFPInterface()

        with pytest.raises(RuntimeError, match="has not been fitted"):
            interface.predict(np.zeros((3, 1)))


class TestPyMCInterface:
    """PyMC model construction is testable without running MCMC."""

    def test_create_spatial_gp_model_builds_pymc_model(self):
        from geo_infer_bayes.api import PyMCInterface

        interface = PyMCInterface()
        X, y = _synthetic_gp_data()

        model = interface.create_spatial_gp_model(X, y)

        assert type(model).__name__ == "Model"
        assert pm is not None
        assert interface.pymc_model is model
        assert "y_obs" in model.named_vars

    def test_create_spatial_gp_model_unknown_kernel_raises(self):
        from geo_infer_bayes.api import PyMCInterface

        interface = PyMCInterface()
        X, y = _synthetic_gp_data()

        with pytest.raises(ValueError, match="Unknown kernel type"):
            interface.create_spatial_gp_model(X, y, kernel_type="magic")

    def test_create_hierarchical_model_builds_pymc_model(self):
        from geo_infer_bayes.api import PyMCInterface

        interface = PyMCInterface()
        rng = np.random.default_rng(3)
        X = rng.normal(size=(12, 2))
        groups = np.array([0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2])
        y = rng.normal(size=12)

        model = interface.create_hierarchical_model(X, y, groups)

        assert type(model).__name__ == "Model"
        assert pm is not None
        assert interface.pymc_model is model
        assert interface._model_type == "hierarchical"
        assert "alpha" in model.named_vars
        assert "beta" in model.named_vars

    def test_sample_without_model_raises_value_error(self):
        from geo_infer_bayes.api import PyMCInterface

        interface = PyMCInterface()

        with pytest.raises(ValueError, match="No PyMC model defined"):
            interface.sample(n_samples=10, n_warmup=5)

    def test_predict_before_sampling_raises_value_error(self):
        from geo_infer_bayes.api import PyMCInterface

        interface = PyMCInterface()
        X, y = _synthetic_gp_data()
        interface.create_spatial_gp_model(X, y)

        with pytest.raises(ValueError, match="No samples available"):
            interface.predict(X)
