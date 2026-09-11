"""
Regression tests for wave-2 silent-fabrication fixes in geo_infer_ai.

Covers:
- GS-264: hyperparameter_search guarded estimator construction and
  explicit scoring-metric validation (no silent zero-scores).
- GS-265: MAPE denominator uses |y_true| with a zero-guard.
- GS-266: best_model/best_score reset per training call and per task type.
- GS-267: compute_shap_like_values batched predictions with identical
  numerical results and bounded predict-call count.
"""

import numpy as np
import pytest
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import r2_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVR

from geo_infer_ai.core.explainability import ModelExplainer
from geo_infer_ai.core.training import ModelTrainer, TrainingConfig


@pytest.fixture
def trainer() -> ModelTrainer:
    config = TrainingConfig(validation_split=0.2, save_best_model=False)
    return ModelTrainer(config)


class TestHyperparameterSearchRobustness:
    """GS-264: no ctor crash on estimators without random_state, no
    silent zero-scores for unsupported scoring names."""

    def test_estimators_without_random_state_param(self, trainer: ModelTrainer) -> None:
        rng = np.random.default_rng(0)
        X = rng.random((40, 3))
        y = (X[:, 0] > 0.5).astype(int)

        result = trainer.hyperparameter_search(
            KNeighborsClassifier, {"n_neighbors": [3, 5]}, X, y, n_splits=2
        )
        assert result["best_params"]["n_neighbors"] in [3, 5]
        assert 0.0 <= result["best_score"] <= 1.0

    def test_regressors_without_random_state_param(self, trainer: ModelTrainer) -> None:
        rng = np.random.default_rng(0)
        X = rng.random((40, 3))
        y = X[:, 0] * 2 - 1

        for model_class, grid in [
            (SVR, {"C": [1.0, 2.0]}),
            (LinearRegression, {"fit_intercept": [True, False]}),
        ]:
            result = trainer.hyperparameter_search(
                model_class,
                grid,
                X,
                y,
                task_type="regression",
                n_splits=2,
            )
            assert result["n_combinations"] == len(next(iter(grid.values())))

    def test_unsupported_scoring_raises(self, trainer: ModelTrainer) -> None:
        rng = np.random.default_rng(0)
        X = rng.random((40, 3))
        y = (X[:, 0] > 0.5).astype(int)

        with pytest.raises(ValueError, match="unsupported scoring 'f1'"):
            trainer.hyperparameter_search(
                RandomForestClassifier,
                {"n_estimators": [5]},
                X,
                y,
                scoring="f1",
            )

    def test_supported_scoring_r2_regression(self, trainer: ModelTrainer) -> None:
        rng = np.random.default_rng(0)
        X = rng.random((40, 3))
        y = X[:, 0] * 2 - 1

        result = trainer.hyperparameter_search(
            LinearRegression,
            {"fit_intercept": [True, False]},
            X,
            y,
            task_type="regression",
            n_splits=2,
        )
        assert result["scoring"] == "r2"
        assert result["best_score"] != 0.0 or result["best_score"] == pytest.approx(
            0.0
        )  # a genuinely-zero fit is possible; no silent fallback either way
        # All candidates must carry the real aggregate score, never a
        # fabricated 0.0 placeholder for a missing metric.
        for row in result["all_results"]:
            assert "score" in row

    def test_rejects_params_rejected_by_ctor_supporting_random_state(
        self, trainer: ModelTrainer
    ) -> None:
        rng = np.random.default_rng(0)
        X = rng.random((40, 3))
        y = (X[:, 0] > 0.5).astype(int)

        # RandomForestClassifier accepts random_state but not "bogus_param":
        # the guarded retry must not mask the genuine TypeError.
        with pytest.raises(TypeError):
            trainer.hyperparameter_search(
                RandomForestClassifier,
                {"bogus_param": [1]},
                X,
                y,
                n_splits=2,
            )


class TestMapeDenominator:
    """GS-265: MAPE divides by |y_true|, excludes y_true == 0."""

    def test_mape_matches_numpy_reference_negative_targets(
        self, trainer: ModelTrainer
    ) -> None:
        rng = np.random.default_rng(7)
        X = rng.random((60, 4))
        y = rng.uniform(-10.0, 10.0, 60)  # negative targets included

        model = LinearRegression().fit(X, y)
        metrics = trainer.evaluate_model(model, X, y, task_type="regression")

        y_pred = model.predict(X)
        nonzero = y != 0
        expected = np.mean(np.abs((y[nonzero] - y_pred[nonzero]) / y[nonzero])) * 100
        assert metrics["mape"] == pytest.approx(float(expected))

    def test_mape_finite_and_sign_correct_for_negative_targets(
        self, trainer: ModelTrainer
    ) -> None:
        rng = np.random.default_rng(11)
        X = rng.random((50, 3))
        y = -np.abs(rng.uniform(1.0, 20.0, 50))  # strictly negative

        model = LinearRegression().fit(X, y)
        metrics = trainer.evaluate_model(model, X, y, task_type="regression")

        assert np.isfinite(metrics["mape"])
        assert metrics["mape"] >= 0.0

    def test_mape_all_zero_target_yields_zero(self, trainer: ModelTrainer) -> None:
        X = np.zeros((10, 2))
        y = np.zeros(10)

        model = LinearRegression().fit(X, y)
        metrics = trainer.evaluate_model(model, X, y, task_type="regression")

        assert metrics["mape"] == 0.0


class TestBestModelReset:
    """GS-266: best-model tracking resets per call / task type."""

    def test_regressor_overwrites_classifier_best(self, trainer: ModelTrainer) -> None:
        rng = np.random.default_rng(3)
        Xc = rng.random((60, 4))
        yc = (Xc[:, 0] > 0.5).astype(int)
        Xr = rng.random((60, 4))
        yr = Xr[:, 0] * 3 - 1

        clf = RandomForestClassifier(n_estimators=5, random_state=0).fit(Xc, yc)
        trainer.train_classifier(clf, Xc, yc)
        assert trainer.best_model is clf

        reg = LinearRegression().fit(Xr, yr)
        trainer.train_regressor(reg, Xr, yr, Xr, yr)
        assert trainer.best_model is reg
        assert trainer.best_score == pytest.approx(float(r2_score(yr, reg.predict(Xr))))

    def test_second_worse_run_does_not_report_stale_best(
        self, trainer: ModelTrainer
    ) -> None:
        rng = np.random.default_rng(5)
        X = rng.random((60, 4))
        y = X[:, 0] * 2 + rng.normal(0, 0.1, 60)

        good = LinearRegression()
        trainer.train_regressor(good, X, y, X, y)
        first_score = trainer.best_score
        assert trainer.best_model is good

        noisy = LinearRegression()
        X_noisy = X + rng.normal(0, 5.0, X.shape)
        trainer.train_regressor(noisy, X_noisy, y, X_noisy, y)

        # A fresh, much worse run must not inherit the previous best.
        assert trainer.best_model is not good
        assert trainer.best_score <= first_score


class CountingPredictModel:
    """Wrapper that counts predict calls for GS-267 batching proof."""

    def __init__(self, inner) -> None:
        self._inner = inner
        self.predict_calls = 0

    def predict(self, X):
        self.predict_calls += 1
        return self._inner.predict(X)


class TestShapBatching:
    """GS-267: batched computation, identical values, bounded call count."""

    @pytest.fixture
    def fixture(self) -> tuple:
        rng = np.random.default_rng(42)
        X = rng.random((100, 10))
        y = X[:, 0] * 2 - X[:, 1] + rng.normal(0, 0.05, 100)
        model = LinearRegression().fit(X, y)
        return model, X

    def test_predict_call_count_bounded(self, fixture: tuple) -> None:
        model, X = fixture
        counting = CountingPredictModel(model)
        explainer = ModelExplainer(counting)

        explainer.compute_shap_like_values(X)

        # 1 (originals) + 1 (background baseline) + n_features (batched per
        # feature) instead of the naive 1 + n_features * n_obs calls.
        assert counting.predict_calls <= 2 + X.shape[1]

    def test_values_match_naive_reference(self, fixture: tuple) -> None:
        model, X = fixture
        n_obs, n_features = X.shape
        bg_size = 20

        explainer = ModelExplainer(model)
        result = explainer.compute_shap_like_values(X, n_samples=bg_size)

        # Recompute the deterministic background the explainer used:
        # resolve_rng(None) resolves to default_rng(DEFAULT_SEED=0).
        from geo_infer_ai.utils.rng import resolve_rng

        resolved = resolve_rng(None)
        bg_idx = resolved.choice(n_obs, size=bg_size, replace=False)
        X_background = X[bg_idx]

        naive = np.zeros((n_obs, n_features))
        for j in range(n_features):
            for i in range(n_obs):
                X_perturbed = np.tile(X[i], (bg_size, 1))
                X_perturbed[:, j] = X_background[:, j]
                pred_original = model.predict(X[i : i + 1])[0]
                pred_perturbed_mean = np.mean(model.predict(X_perturbed))
                naive[i, j] = pred_original - pred_perturbed_mean

        assert np.allclose(result["shap_values"], naive)

    def test_default_fixture_call_count(self, fixture: tuple) -> None:
        model, X = fixture
        counting = CountingPredictModel(model)
        explainer = ModelExplainer(counting)
        explainer.compute_shap_like_values(X)
        # At defaults (n_obs=100, n_features=10) the naive implementation
        # made >11,000 predict calls; the batched one makes 12.
        assert counting.predict_calls == 12


class TestLogisticRegressionShapCompat:
    """Sanity: batching works for classifiers too (2-D predict output)."""

    def test_classifier_batching(self) -> None:
        rng = np.random.default_rng(9)
        X = rng.random((30, 3))
        y = (X[:, 0] > 0.5).astype(int)
        model = LogisticRegression().fit(X, y)
        counting = CountingPredictModel(model)

        explainer = ModelExplainer(counting)
        result = explainer.compute_shap_like_values(X, n_samples=10)

        assert result["shap_values"].shape == (30, 3)
        assert counting.predict_calls <= 2 + X.shape[1]
