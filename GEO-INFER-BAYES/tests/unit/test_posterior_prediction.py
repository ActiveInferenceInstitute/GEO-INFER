"""Tests for posterior-predictive machinery across the BAYES models.

Three defects these pin down, each of which passed the previous suite:

* Draw counting -- ``len(posterior.samples)`` is the number of parameter
  *names*, so using it silently collapsed a 4000-draw posterior to 3 draws.
* Predictive variance -- averaging only the spread of per-draw means omits the
  conditional variance of each draw, so intervals came out far too narrow.
* Draw selection -- taking the first N draws weights the least-converged part
  of a chain most heavily.
"""

from __future__ import annotations

import numpy as np
import pytest

from geo_infer_bayes.core.inference import BayesianInference
from geo_infer_bayes.core.posterior import PosteriorAnalysis
from geo_infer_bayes.models import SpatialGP
from geo_infer_bayes.models._model_utils import posterior_draw_indices
from geo_infer_bayes.models.hierarchical import HierarchicalBayesianModel
from geo_infer_bayes.models.multilevel import MultilevelModel


class _FakePosterior:
    """Minimal stand-in exposing only the ``samples`` mapping models read."""

    def __init__(self, samples: dict) -> None:
        self.samples = samples


@pytest.fixture
def gp_data() -> tuple[np.ndarray, np.ndarray]:
    """A small realization of an RBF Gaussian process with known parameters."""
    rng = np.random.default_rng(0)
    X = rng.uniform(0, 10, size=(25, 2))
    sq_dist = np.sum((X[:, None, :] - X[None, :, :]) ** 2, axis=-1)
    cov = 1.5 * np.exp(-0.5 * sq_dist / 2.0**2) + 1e-8 * np.eye(25)
    y = rng.multivariate_normal(np.zeros(25), cov)
    return X, y + rng.normal(0, 0.1, size=25)


@pytest.fixture
def gp_posterior() -> _FakePosterior:
    """40 hyperparameter draws that straddle the truth."""
    rng = np.random.default_rng(1)
    return _FakePosterior(
        {
            "lengthscale": rng.uniform(1.5, 2.5, size=40),
            "variance": rng.uniform(1.0, 2.0, size=40),
            "noise": rng.uniform(0.005, 0.02, size=40),
        }
    )


class TestPosteriorDrawIndices:
    def test_uses_the_draw_axis_not_the_parameter_count(self) -> None:
        posterior = _FakePosterior({"a": np.zeros(500), "b": np.zeros(500)})
        indices = posterior_draw_indices(posterior, 100, ["a", "b"])
        assert len(indices) == 100

    def test_caps_at_the_shortest_parameter(self) -> None:
        posterior = _FakePosterior({"a": np.zeros(50), "b": np.zeros(30)})
        indices = posterior_draw_indices(posterior, 100, ["a", "b"])
        assert len(indices) == 30
        assert indices.max() == 29

    def test_draws_span_the_whole_chain(self) -> None:
        posterior = _FakePosterior({"a": np.zeros(1000)})
        indices = posterior_draw_indices(posterior, 10, ["a"])
        assert indices[0] == 0
        assert indices[-1] == 999
        assert np.all(np.diff(indices) > 0)

    def test_missing_parameter_is_reported(self) -> None:
        with pytest.raises(ValueError, match="no samples for parameter"):
            posterior_draw_indices(_FakePosterior({"a": np.zeros(5)}), 3, ["b"])

    def test_empty_posterior_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="no usable parameter samples"):
            posterior_draw_indices(_FakePosterior({"a": np.zeros(0)}), 3, ["a"])

    def test_non_positive_sample_count_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="samples must be greater"):
            posterior_draw_indices(_FakePosterior({"a": np.zeros(5)}), 0, ["a"])


class TestSpatialGpPosteriorPredict:
    def test_averages_over_the_requested_number_of_draws(
        self, gp_data: tuple, gp_posterior: _FakePosterior
    ) -> None:
        """Asking for more draws than the old 3-parameter cap must matter."""
        X, y = gp_data
        model = SpatialGP(kernel="rbf", lengthscale=2.0, variance=1.5, noise=0.01)
        model.fit(X, y)
        few = model.predict(X[:5], posterior=gp_posterior, samples=3)
        many = model.predict(X[:5], posterior=gp_posterior, samples=40)
        assert not np.allclose(few, many)

    def test_predictive_std_includes_the_conditional_variance(
        self, gp_data: tuple, gp_posterior: _FakePosterior
    ) -> None:
        """Away from the data the interval must be wide, not near zero."""
        X, y = gp_data
        model = SpatialGP(kernel="rbf", lengthscale=2.0, variance=1.5, noise=0.01)
        model.fit(X, y)
        far = np.array([[100.0, 100.0]])
        _, std = model.predict(far, posterior=gp_posterior, samples=20, return_std=True)
        # With no nearby data the predictive sd must approach the prior sd,
        # sqrt(variance) ~ 1.0-1.4 over these draws.
        assert std[0] > 0.9

    def test_predictive_std_is_calibrated_on_held_out_points(
        self, gp_posterior: _FakePosterior
    ) -> None:
        """A 95% interval must cover roughly 95% of held-out observations."""
        rng = np.random.default_rng(5)
        X = rng.uniform(0, 10, size=(120, 2))
        sq_dist = np.sum((X[:, None, :] - X[None, :, :]) ** 2, axis=-1)
        cov = 1.5 * np.exp(-0.5 * sq_dist / 4.0) + 1e-8 * np.eye(120)
        latent = rng.multivariate_normal(np.zeros(120), cov)
        y = latent + rng.normal(0, 0.1, size=120)

        model = SpatialGP(kernel="rbf", lengthscale=2.0, variance=1.5, noise=0.01)
        model.fit(X[:90], y[:90])
        mean, std = model.predict(
            X[90:], posterior=gp_posterior, samples=30, return_std=True
        )
        total_sd = np.sqrt(std**2 + 0.01)
        covered = np.mean(np.abs(y[90:] - mean) <= 1.96 * total_sd)
        assert covered > 0.8

    def test_the_fitted_state_survives_posterior_prediction(
        self, gp_data: tuple, gp_posterior: _FakePosterior
    ) -> None:
        """Adopting draws must not leave the model on someone else's kernel."""
        X, y = gp_data
        model = SpatialGP(kernel="rbf", lengthscale=2.0, variance=1.5, noise=0.01)
        model.fit(X, y)
        before = (model.lengthscale, model.variance, model.noise, model.L.copy())
        model.predict(X[:3], posterior=gp_posterior, samples=10, return_std=True)
        assert (model.lengthscale, model.variance, model.noise) == before[:3]
        np.testing.assert_array_equal(model.L, before[3])

    def test_unfitted_model_is_rejected(self, gp_posterior: _FakePosterior) -> None:
        model = SpatialGP(kernel="rbf")
        with pytest.raises(ValueError, match="has not been fitted"):
            model.predict(np.zeros((2, 2)), posterior=gp_posterior)

    def test_posterior_predictive_uses_all_requested_draws(
        self, gp_data: tuple, gp_posterior: _FakePosterior
    ) -> None:
        X, y = gp_data
        model = SpatialGP(kernel="rbf", lengthscale=2.0, variance=1.5, noise=0.01)
        model.fit(X, y)
        draws = model.posterior_predictive(
            gp_posterior, X=X[:4], samples=25, random_seed=3
        )
        assert draws.shape == (25, 4)

    def test_posterior_predictive_is_replayable(
        self, gp_data: tuple, gp_posterior: _FakePosterior
    ) -> None:
        X, y = gp_data
        model = SpatialGP(kernel="rbf", lengthscale=2.0, variance=1.5, noise=0.01)
        model.fit(X, y)
        a = model.posterior_predictive(gp_posterior, X=X[:4], samples=8, random_seed=1)
        b = model.posterior_predictive(gp_posterior, X=X[:4], samples=8, random_seed=1)
        np.testing.assert_array_equal(a, b)

    def test_posterior_predictive_is_wider_than_the_latent_prediction(
        self, gp_data: tuple, gp_posterior: _FakePosterior
    ) -> None:
        """Observation draws carry noise the latent prediction does not."""
        X, y = gp_data
        model = SpatialGP(kernel="rbf", lengthscale=2.0, variance=1.5, noise=0.01)
        model.fit(X, y)
        far = np.tile([[50.0, 50.0]], (1, 1))
        _, latent_std = model.predict(
            far, posterior=gp_posterior, samples=30, return_std=True
        )
        draws = model.posterior_predictive(
            gp_posterior, X=far, samples=400, random_seed=2
        )
        assert draws.std() > latent_std[0] * 0.9


class TestPointwiseLogLikelihood:
    def test_sums_to_the_joint_marginal_likelihood(self, gp_data: tuple) -> None:
        """The ordered-conditional decomposition is exact, not an approximation."""
        X, y = gp_data
        model = SpatialGP(kernel="rbf", lengthscale=2.0, variance=1.5, noise=0.01)
        theta = {"lengthscale": 2.0, "variance": 1.5, "noise": 0.01}
        pointwise = model.pointwise_log_likelihood(theta, {"X": X, "y": y})
        assert pointwise.shape == (len(y),)
        assert pointwise.sum() == pytest.approx(
            model.log_likelihood(theta, {"X": X, "y": y})
        )

    def test_distinguishes_kernels(self, gp_data: tuple) -> None:
        """Per-point marginals would score every stationary kernel the same."""
        X, y = gp_data
        theta = {"lengthscale": 2.0, "variance": 1.5, "noise": 0.01}
        right = SpatialGP(kernel="rbf").pointwise_log_likelihood(
            theta, {"X": X, "y": y}
        )
        wrong = SpatialGP(kernel="exponential").pointwise_log_likelihood(
            theta, {"X": X, "y": y}
        )
        assert right.sum() > wrong.sum()

    def test_leaves_model_parameters_untouched(self, gp_data: tuple) -> None:
        X, y = gp_data
        model = SpatialGP(kernel="rbf", lengthscale=1.0, variance=1.0, noise=0.1)
        model.pointwise_log_likelihood(
            {"lengthscale": 9.0, "variance": 9.0, "noise": 9.0}, {"X": X, "y": y}
        )
        assert (model.lengthscale, model.variance, model.noise) == (1.0, 1.0, 0.1)

    def test_non_positive_definite_covariance_gives_minus_infinity(
        self, gp_data: tuple
    ) -> None:
        X, y = gp_data
        model = SpatialGP(kernel="rbf")
        result = model.pointwise_log_likelihood(
            {"lengthscale": 1.0, "variance": -5.0, "noise": 0.0}, {"X": X, "y": y}
        )
        assert np.all(np.isneginf(result))


class TestHierarchicalPrediction:
    def test_uses_the_full_draw_axis(self) -> None:
        """The model has 3 alpha parameters; draws must not be capped at 3."""
        model = HierarchicalBayesianModel(n_levels=3)
        rng = np.random.default_rng(0)
        posterior = _FakePosterior(
            {f"alpha_{i}": rng.normal(i, 1.0, size=200) for i in range(3)}
            | {"noise": rng.uniform(0.5, 1.5, size=200)}
        )
        mean, std = model.predict(
            np.zeros(4), posterior=posterior, samples=150, return_std=True
        )
        assert mean.shape == (4,)
        # alpha_0 has mean 0 and sd 1; 150 draws pins the mean near 0, while
        # the old 3-draw cap left it far off.
        assert abs(mean[0]) < 0.3
        assert std[0] == pytest.approx(1.0, abs=0.2)

    def test_requires_a_posterior(self) -> None:
        model = HierarchicalBayesianModel(n_levels=2)
        with pytest.raises(RuntimeError, match="requires a posterior"):
            model.predict(np.zeros(3))

    def test_posterior_predictive_shape_and_replay(self) -> None:
        model = HierarchicalBayesianModel(n_levels=2)
        rng = np.random.default_rng(2)
        posterior = _FakePosterior(
            {
                "alpha_0": rng.normal(0, 1, size=60),
                "alpha_1": rng.normal(1, 1, size=60),
                "noise": rng.uniform(0.5, 1.5, size=60),
            }
        )
        a = model.posterior_predictive(
            posterior, X=np.zeros(5), samples=20, random_seed=7
        )
        b = model.posterior_predictive(
            posterior, X=np.zeros(5), samples=20, random_seed=7
        )
        assert a.shape == (20, 5)
        np.testing.assert_array_equal(a, b)


class TestMultilevelPrediction:
    def test_global_mean_and_level_effects_come_from_the_same_draw(self) -> None:
        """Mismatched indexing across parameters would break this identity."""
        model = MultilevelModel(levels=["global", "regional"])
        # Effects perfectly anti-correlated with the global mean, so a matched
        # draw always sums to zero and a mismatched one does not.
        global_mean = np.arange(50, dtype=float)
        posterior = _FakePosterior(
            {
                "global_mean": global_mean,
                "regional_effects": -global_mean[:, None] * np.ones((50, 2)),
                "noise": np.full(50, 0.25),
            }
        )
        mean = model.predict(
            np.zeros(2),
            posterior=posterior,
            samples=50,
            level_indices={"regional": np.array([0, 1])},
        )
        np.testing.assert_allclose(mean, np.zeros(2), atol=1e-9)

    def test_uses_the_requested_number_of_draws(self) -> None:
        model = MultilevelModel(levels=["global", "regional"])
        rng = np.random.default_rng(4)
        posterior = _FakePosterior(
            {
                "global_mean": rng.normal(3.0, 1.0, size=400),
                "noise": rng.uniform(0.5, 1.5, size=400),
            }
        )
        mean, std = model.predict(
            np.zeros(3), posterior=posterior, samples=300, return_std=True
        )
        assert mean[0] == pytest.approx(3.0, abs=0.2)
        assert std[0] == pytest.approx(1.0, abs=0.2)

    def test_posterior_predictive_requires_x(self) -> None:
        model = MultilevelModel()
        posterior = _FakePosterior({"global_mean": np.zeros(5), "noise": np.ones(5)})
        with pytest.raises(ValueError, match="X is required"):
            model.posterior_predictive(posterior)

    def test_posterior_predictive_is_replayable(self) -> None:
        model = MultilevelModel(levels=["global", "regional"])
        posterior = _FakePosterior(
            {"global_mean": np.zeros(30), "noise": np.full(30, 0.5)}
        )
        a = model.posterior_predictive(
            posterior, X=np.zeros(4), samples=10, random_seed=1
        )
        b = model.posterior_predictive(
            posterior, X=np.zeros(4), samples=10, random_seed=1
        )
        np.testing.assert_array_equal(a, b)


class TestChainIdentity:
    def test_chain_samples_recovers_the_chain_axis(self) -> None:
        model = SpatialGP(kernel="rbf")
        samples = {"lengthscale": np.arange(40, dtype=float)}
        posterior = PosteriorAnalysis(model, samples, None, "mcmc", n_chains=4)
        chains = posterior.chain_samples()
        assert chains["lengthscale"].shape == (4, 10)
        np.testing.assert_array_equal(chains["lengthscale"][0], np.arange(10.0))
        np.testing.assert_array_equal(
            chains["lengthscale"][3], np.arange(30.0, 40.0)
        )

    def test_r_hat_is_defined_once_chains_are_declared(self) -> None:
        """Pooling chains makes R-hat undefined; ArviZ then reports NaN."""
        model = SpatialGP(kernel="rbf")
        rng = np.random.default_rng(0)
        samples = {"lengthscale": rng.normal(2.0, 0.1, size=400)}
        pooled = PosteriorAnalysis(model, samples, None, "mcmc")
        split = PosteriorAnalysis(model, samples, None, "mcmc", n_chains=4)
        assert np.isnan(pooled.summary()["r_hat"].iloc[0])
        assert split.summary()["r_hat"].iloc[0] == pytest.approx(1.0, abs=0.05)

    def test_ragged_draw_count_is_rejected(self) -> None:
        model = SpatialGP(kernel="rbf")
        posterior = PosteriorAnalysis(
            model, {"lengthscale": np.zeros(10)}, None, "mcmc", n_chains=4
        )
        with pytest.raises(ValueError, match="not divisible by n_chains"):
            posterior.chain_samples()

    def test_bad_chain_count_is_rejected(self) -> None:
        model = SpatialGP(kernel="rbf")
        with pytest.raises(ValueError, match="n_chains must be a positive integer"):
            PosteriorAnalysis(model, {"a": np.zeros(4)}, None, "mcmc", n_chains=0)


class TestInferenceBindsTrainingData:
    def test_a_gp_can_predict_straight_after_inference(self) -> None:
        """A posterior is conditional on data; the model must retain it."""
        rng = np.random.default_rng(0)
        X = rng.uniform(0, 10, size=(20, 2))
        y = rng.normal(0, 1, size=20)
        model = SpatialGP(kernel="rbf", lengthscale=2.0, variance=1.0, noise=0.1)
        assert model.X_train is None

        inference = BayesianInference(
            model=model, method="mcmc", sampler_config={"n_chains": 2, "random_seed": 0}
        )
        posterior = inference.run(
            data={"X": X, "y": y}, n_samples=40, n_warmup=10, progress_bar=False
        )
        assert model.X_train is not None
        assert posterior.n_chains == 2
        # The prediction call is the point: it raised before the data was bound.
        mean = posterior.predict(X[:3], samples=10)
        assert mean.shape == (3,)

    def test_non_chain_backends_report_a_single_chain(self) -> None:
        """SMC has no chains, so its draws are one pooled sample."""
        model = SpatialGP(kernel="rbf", lengthscale=2.0, variance=1.0, noise=0.1)
        inference = BayesianInference(
            model=model, method="smc", sampler_config={"random_seed": 0}
        )
        assert inference._backend_chain_count() == 1

    def test_bind_training_data_is_a_no_op_for_unshaped_data(self) -> None:
        """A model conditioned on something other than X/y must still run."""
        model = SpatialGP(kernel="rbf")
        model.bind_training_data({"observations": np.zeros(3)})
        assert model.X_train is None
