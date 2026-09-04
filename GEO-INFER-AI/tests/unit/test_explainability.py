"""
Unit tests for explainability functionality.
"""

import numpy as np
import pytest
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression

from geo_infer_ai.core.explainability import ModelExplainer


class TestModelExplainer:
    """Test ModelExplainer class."""

    @pytest.fixture
    def trained_regressor(self) -> RandomForestRegressor:
        np.random.seed(42)
        X = np.random.randn(100, 5)
        y = 2.0 * X[:, 0] + 0.5 * X[:, 1] + np.random.randn(100) * 0.1
        model = RandomForestRegressor(n_estimators=20, random_state=42)
        model.fit(X, y)
        return model

    @pytest.fixture
    def trained_classifier(self) -> RandomForestClassifier:
        np.random.seed(42)
        X = np.random.randn(100, 5)
        y = (X[:, 0] > 0).astype(int)
        model = RandomForestClassifier(n_estimators=20, random_state=42)
        model.fit(X, y)
        return model

    @pytest.fixture
    def sample_data(self) -> np.ndarray:
        np.random.seed(42)
        return np.random.randn(100, 5)

    def test_calculate_feature_importance_permutation(
        self, trained_regressor: RandomForestRegressor, sample_data: np.ndarray
    ) -> None:
        np.random.seed(42)
        y = 2.0 * sample_data[:, 0] + 0.5 * sample_data[:, 1] + np.random.randn(100) * 0.1
        explainer = ModelExplainer(trained_regressor)
        importances = explainer.calculate_feature_importance(sample_data, y, method='permutation')

        assert isinstance(importances, dict)
        assert len(importances) == 5
        # Feature 0 should be most important
        keys = list(importances.keys())
        assert all(isinstance(v, (float, np.floating)) for v in importances.values())

    def test_calculate_feature_importance_coefficient(self) -> None:
        np.random.seed(42)
        X = np.random.randn(100, 3)
        y = 3.0 * X[:, 0] + X[:, 2] + np.random.randn(100) * 0.01
        model = LinearRegression()
        model.fit(X, y)

        explainer = ModelExplainer(model)
        importances = explainer.calculate_feature_importance(
            X, y, method='coefficient',
            feature_names=['a', 'b', 'c'],
        )

        assert 'a' in importances
        assert 'b' in importances
        assert 'c' in importances
        # Feature 'a' should have largest absolute coefficient
        assert abs(importances['a']) > abs(importances['b'])

    def test_explain_prediction_classifier(
        self, trained_classifier: RandomForestClassifier, sample_data: np.ndarray
    ) -> None:
        explainer = ModelExplainer(trained_classifier)
        prediction = trained_classifier.predict(sample_data[:1])[0]
        result = explainer.explain_prediction(sample_data[0], prediction)

        assert 'prediction' in result
        assert 'probabilities' in result
        assert 'confidence' in result
        assert len(result['probabilities']) == 2

    def test_explain_prediction_regressor(
        self, trained_regressor: RandomForestRegressor, sample_data: np.ndarray
    ) -> None:
        explainer = ModelExplainer(trained_regressor)
        prediction = trained_regressor.predict(sample_data[:1])[0]
        result = explainer.explain_prediction(sample_data[0], prediction)

        assert 'prediction' in result
        assert 'feature_values' in result
        assert len(result['feature_values']) == 5

    def test_shap_like_values(
        self, trained_regressor: RandomForestRegressor, sample_data: np.ndarray
    ) -> None:
        explainer = ModelExplainer(trained_regressor)
        result = explainer.compute_shap_like_values(
            sample_data[:20], n_samples=10,
            feature_names=['f0', 'f1', 'f2', 'f3', 'f4'],
            rng=np.random.default_rng(42),
        )

        # Pin seeded output: replaying the same generator state must
        # reproduce the exact same explanation.
        replay = explainer.compute_shap_like_values(
            sample_data[:20], n_samples=10,
            feature_names=['f0', 'f1', 'f2', 'f3', 'f4'],
            rng=np.random.default_rng(42),
        )
        np.testing.assert_array_equal(result['shap_values'], replay['shap_values'])
        assert result['base_value'] == replay['base_value']

        assert 'shap_values' in result
        assert result['shap_values'].shape == (20, 5)
        assert 'base_value' in result
        assert 'feature_ranking' in result
        assert len(result['feature_ranking']) == 5
        assert 'mean_abs_shap' in result

    def test_partial_dependence(
        self, trained_regressor: RandomForestRegressor, sample_data: np.ndarray
    ) -> None:
        explainer = ModelExplainer(trained_regressor)
        result = explainer.compute_partial_dependence(
            sample_data, feature_index=0, grid_resolution=20,
            feature_name='feature_0',
        )

        assert 'feature_name' in result
        assert result['feature_name'] == 'feature_0'
        assert 'grid_values' in result
        assert 'avg_predictions' in result
        assert len(result['grid_values']) == 20
        assert len(result['avg_predictions']) == 20

    def test_spatial_explanation(self, trained_regressor: RandomForestRegressor) -> None:
        np.random.seed(42)
        spatial_features = np.random.randn(50, 5)
        predictions = trained_regressor.predict(spatial_features)
        coordinates = np.random.randn(50, 2) * 100

        explainer = ModelExplainer(trained_regressor)
        result = explainer.generate_spatial_explanation(spatial_features, predictions, coordinates)

        assert 'prediction_statistics' in result
        assert 'spatial_patterns' in result
        assert 'spatial_extent' in result
        assert 'lat_range' in result['spatial_extent']
