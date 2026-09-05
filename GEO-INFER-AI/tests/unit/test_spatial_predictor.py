"""
Unit tests for spatial predictor.
"""

import numpy as np
import pandas as pd
import pytest

import geo_infer_ai
from geo_infer_ai.models import IDWInterpolator, OrdinaryKriging, SpatialPredictor
from geo_infer_ai.models.predictive.spatial_predictor import SpatialPredictor


class TestSpatialPredictor:
    """Test SpatialPredictor class."""

    @pytest.fixture
    def regression_data(self) -> tuple:
        """Create regression test data."""
        np.random.seed(42)
        X = np.random.randn(100, 5)
        y = np.random.randn(100)
        coordinates = np.random.randn(100, 2)  # lon, lat
        return X, y, coordinates

    def test_init_linear(self) -> None:
        """Test initialization with linear model."""
        predictor = SpatialPredictor(model_type="linear")
        assert predictor.model_type == "linear"
        assert predictor.model is not None

    def test_init_random_forest(self) -> None:
        """Test initialization with Random Forest."""
        predictor = SpatialPredictor(model_type="random_forest")
        assert predictor.model_type == "random_forest"
        assert predictor.model is not None

    def test_init_invalid_type(self) -> None:
        """Test initialization with invalid model type."""
        with pytest.raises(ValueError, match="Unknown model_type"):
            SpatialPredictor(model_type="invalid")

    def test_fit_predict_numpy(self, regression_data: tuple) -> None:
        """Test fit and predict with numpy arrays."""
        X, y, coordinates = regression_data
        predictor = SpatialPredictor(model_type="random_forest", include_spatial_features=True)
        predictor.fit(X, y, coordinates=coordinates)

        predictions = predictor.predict(X, coordinates=coordinates)
        assert len(predictions) == len(y)
        assert all(np.isfinite(pred) for pred in predictions)

    def test_fit_predict_dataframe(self, regression_data: tuple) -> None:
        """Test fit and predict with pandas DataFrame."""
        X, y, coordinates = regression_data
        X_df = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(X.shape[1])])

        predictor = SpatialPredictor(model_type="random_forest", include_spatial_features=False)
        predictor.fit(X_df, y)

        predictions = predictor.predict(X_df)
        assert len(predictions) == len(y)

    def test_feature_importance(self, regression_data: tuple) -> None:
        """Test feature importance extraction."""
        X, y, coordinates = regression_data
        predictor = SpatialPredictor(model_type="random_forest", include_spatial_features=False)
        predictor.fit(X, y)

        importance = predictor.get_feature_importance()
        assert importance is not None
        assert len(importance) >= X.shape[1]  # May include spatial features

    def test_spatial_features(self, regression_data: tuple) -> None:
        """Test that spatial features are added when requested."""
        X, y, coordinates = regression_data

        predictor_with_spatial = SpatialPredictor(
            model_type="random_forest", include_spatial_features=True
        )
        predictor_with_spatial.fit(X, y, coordinates=coordinates)

        predictor_without_spatial = SpatialPredictor(
            model_type="random_forest", include_spatial_features=False
        )
        predictor_without_spatial.fit(X, y)

        # Models should have different feature counts
        importance_with = predictor_with_spatial.get_feature_importance()
        importance_without = predictor_without_spatial.get_feature_importance()

        assert importance_with is not None
        assert importance_without is not None
        assert len(importance_with) > len(importance_without)

    def test_predict_before_fit(self, regression_data: tuple) -> None:
        """Test that prediction fails before training."""
        from sklearn.exceptions import NotFittedError
        
        X, y, coordinates = regression_data
        predictor = SpatialPredictor(model_type="random_forest")

        # sklearn raises NotFittedError, which our code converts to ValueError
        with pytest.raises((ValueError, NotFittedError)):
            predictor.predict(X)



def test_interpolators_exported_publicly() -> None:
    """IDWInterpolator and OrdinaryKriging are part of the public surface."""
    assert geo_infer_ai.IDWInterpolator is IDWInterpolator
    assert geo_infer_ai.OrdinaryKriging is OrdinaryKriging
    assert geo_infer_ai.models.IDWInterpolator is IDWInterpolator
    assert geo_infer_ai.models.OrdinaryKriging is OrdinaryKriging
    assert set(
        ["IDWInterpolator", "OrdinaryKriging", "SpatialPredictor"]
    ).issubset(set(geo_infer_ai.models.__all__))
