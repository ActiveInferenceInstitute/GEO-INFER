"""
Unit tests for feature engineering.
"""

import numpy as np
import pandas as pd
import pytest

from geo_infer_ai.preprocessing.feature_engineering import GeospatialFeatureEngineer


class TestGeospatialFeatureEngineer:
    """Test GeospatialFeatureEngineer class."""

    @pytest.fixture
    def sample_data(self) -> tuple:
        """Create sample test data."""
        np.random.seed(42)
        X = np.random.randn(50, 5)
        coordinates = np.random.randn(50, 2)  # lon, lat
        timestamps = pd.date_range("2023-01-01", periods=50, freq="D")
        return X, coordinates, timestamps

    def test_create_spatial_features(self) -> None:
        """Test spatial feature creation."""
        np.random.seed(42)
        coordinates = np.random.randn(50, 2)

        engineer = GeospatialFeatureEngineer()
        features = engineer.create_spatial_features(coordinates)

        assert isinstance(features, pd.DataFrame)
        assert "longitude" in features.columns
        assert "latitude" in features.columns
        assert "distance_from_centroid" in features.columns
        assert len(features) == 50

    def test_create_spatial_features_with_angles(self) -> None:
        """Test spatial feature creation with angular features."""
        np.random.seed(42)
        coordinates = np.random.randn(50, 2)

        engineer = GeospatialFeatureEngineer()
        features = engineer.create_spatial_features(
            coordinates, include_angles=True
        )

        assert "angle_from_centroid" in features.columns

    def test_create_temporal_features(self) -> None:
        """Test temporal feature creation."""
        timestamps = pd.date_range("2023-01-01", periods=50, freq="D")

        engineer = GeospatialFeatureEngineer()
        features = engineer.create_temporal_features(timestamps)

        assert isinstance(features, pd.DataFrame)
        assert "year" in features.columns
        assert "month" in features.columns
        assert "day" in features.columns
        assert "month_sin" in features.columns
        assert "month_cos" in features.columns
        assert len(features) == 50

    def test_fit_transform_with_spatial(self, sample_data: tuple) -> None:
        """Test fit_transform with spatial features."""
        X, coordinates, _ = sample_data

        engineer = GeospatialFeatureEngineer(normalize=True)
        X_transformed = engineer.fit_transform(X, coordinates=coordinates)

        assert X_transformed.shape[0] == X.shape[0]
        assert X_transformed.shape[1] >= X.shape[1]  # Should have same or more features
        assert engineer.scaler is not None
        assert engineer.feature_names_ is not None

    def test_fit_transform_with_temporal(self, sample_data: tuple) -> None:
        """Test fit_transform with temporal features."""
        X, _, timestamps = sample_data

        engineer = GeospatialFeatureEngineer(normalize=True)
        X_transformed = engineer.fit_transform(X, timestamps=timestamps)

        assert X_transformed.shape[0] == X.shape[0]
        assert X_transformed.shape[1] >= X.shape[1]  # Should have same or more features
        assert engineer.feature_names_ is not None

    def test_fit_transform_without_normalization(self, sample_data: tuple) -> None:
        """Test fit_transform without normalization."""
        X, coordinates, _ = sample_data

        engineer = GeospatialFeatureEngineer(normalize=False)
        X_transformed = engineer.fit_transform(X, coordinates=coordinates)

        assert X_transformed.shape[0] == X.shape[0]
        assert engineer.scaler is None

    def test_transform_after_fit(self, sample_data: tuple) -> None:
        """Test transform after fit_transform."""
        X, coordinates, _ = sample_data
        X_train, X_test = X[:40], X[40:]
        coords_train, coords_test = coordinates[:40], coordinates[40:]

        engineer = GeospatialFeatureEngineer(normalize=True)
        X_train_transformed = engineer.fit_transform(X_train, coordinates=coords_train)
        expected_features = X_train_transformed.shape[1]

        X_test_transformed = engineer.transform(X_test, coordinates=coords_test)

        assert X_test_transformed.shape[0] == len(X_test)
        assert X_test_transformed.shape[1] == expected_features

    def test_transform_before_fit(self, sample_data: tuple) -> None:
        """Test that transform fails before fit."""
        X, coordinates, _ = sample_data

        engineer = GeospatialFeatureEngineer(normalize=True)

        with pytest.raises(ValueError, match="must be fitted"):
            engineer.transform(X, coordinates=coordinates)

    def test_get_feature_names(self, sample_data: tuple) -> None:
        """Test feature name retrieval."""
        X, coordinates, _ = sample_data

        engineer = GeospatialFeatureEngineer()
        engineer.fit_transform(X, coordinates=coordinates)

        feature_names = engineer.get_feature_names()
        assert feature_names is not None
        assert len(feature_names) >= X.shape[1]  # Should have at least original features

