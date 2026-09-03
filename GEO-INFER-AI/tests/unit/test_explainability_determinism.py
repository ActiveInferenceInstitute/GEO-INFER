"""Determinism tests for explainability output.

``ModelExplainer.compute_shap_like_values`` draws a background subsample.
Historically that draw used the process-wide ``numpy.random`` singleton, so
identical inputs could yield different explanations depending on whatever
else had drawn randomness first. The method now accepts an explicit
``rng`` (resolved via the repo-wide ``resolve_rng`` pattern) and resolves
``None`` to a fixed seed, so the same inputs must give byte-identical
explanations.
"""

from __future__ import annotations

import numpy as np
import pytest
from sklearn.ensemble import RandomForestRegressor

from geo_infer_ai.core.explainability import ModelExplainer


@pytest.fixture
def trained_model_and_data() -> tuple[RandomForestRegressor, np.ndarray]:
    """A fixed regressor and a fixed feature matrix."""
    rng = np.random.default_rng(42)
    X = rng.standard_normal((60, 4))
    y = 2.0 * X[:, 0] - X[:, 2] + rng.standard_normal(60) * 0.05
    model = RandomForestRegressor(n_estimators=10, random_state=42)
    model.fit(X, y)
    return model, X


def _explanation(explainer: ModelExplainer, X: np.ndarray, seed: int | None) -> dict:
    rng = np.random.default_rng(seed) if seed is not None else None
    return explainer.compute_shap_like_values(X, n_samples=15, rng=rng)


class TestExplainabilityDeterminism:
    """Same seed (or default) must produce identical explanations."""

    def test_default_rng_is_deterministic(
        self, trained_model_and_data: tuple[RandomForestRegressor, np.ndarray]
    ) -> None:
        model, X = trained_model_and_data
        explainer = ModelExplainer(model)

        first = explainer.compute_shap_like_values(X, n_samples=15)
        second = explainer.compute_shap_like_values(X, n_samples=15)

        np.testing.assert_array_equal(first["shap_values"], second["shap_values"])
        assert first["base_value"] == second["base_value"]
        assert first["mean_abs_shap"] == second["mean_abs_shap"]

    def test_same_seed_gives_identical_explanations(
        self, trained_model_and_data: tuple[RandomForestRegressor, np.ndarray]
    ) -> None:
        model, X = trained_model_and_data
        explainer = ModelExplainer(model)

        first = _explanation(explainer, X, seed=7)
        second = _explanation(explainer, X, seed=7)

        np.testing.assert_array_equal(first["shap_values"], second["shap_values"])
        assert first["base_value"] == second["base_value"]

    def test_sharing_one_generator_is_reproducible(
        self, trained_model_and_data: tuple[RandomForestRegressor, np.ndarray]
    ) -> None:
        """Replaying the same generator state replays the same explanation."""
        model, X = trained_model_and_data
        explainer = ModelExplainer(model)

        def run() -> dict:
            return explainer.compute_shap_like_values(
                X, n_samples=15, rng=np.random.default_rng(123)
            )

        np.testing.assert_array_equal(run()["shap_values"], run()["shap_values"])

    def test_distinct_seeds_draw_distinct_subsamples(
        self, trained_model_and_data: tuple[RandomForestRegressor, np.ndarray]
    ) -> None:
        """A different seed is not silently aliased to the default stream."""
        model, X = trained_model_and_data
        explainer = ModelExplainer(model)

        by_seed = {
            seed: _explanation(explainer, X, seed=seed)["shap_values"]
            for seed in (1, 2)
        }
        assert not np.array_equal(by_seed[1], by_seed[2])
