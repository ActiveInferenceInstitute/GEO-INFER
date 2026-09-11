"""
Coverage-focused unit tests for GeospatialFeatureEngineer edge branches.

Complements ``test_feature_engineering.py``: invalid-centroid validation,
normalization transform paths, and temporal aggregation windows.
"""

import numpy as np
import pandas as pd
import pytest

from geo_infer_ai.preprocessing.feature_engineering import (
    GeospatialFeatureEngineer,
)


class TestCentroidValidation:
    """create_spatial_features validates the centroid contract."""

    def setup_method(self) -> None:
        self.engineer = GeospatialFeatureEngineer()
        self.coordinates = np.array([[0.0, 0.0], [2.0, 2.0], [4.0, 4.0]])

    def test_invalid_centroid_shape_raises(self) -> None:
        with pytest.raises(ValueError, match="two finite coordinates"):
            self.engineer.create_spatial_features(
                self.coordinates, centroid=[1.0, 2.0, 3.0]
            )

    def test_non_finite_centroid_raises(self) -> None:
        with pytest.raises(ValueError, match="two finite coordinates"):
            self.engineer.create_spatial_features(
                self.coordinates, centroid=[np.nan, 0.0]
            )

    def test_explicit_centroid_drives_distances(self) -> None:
        features = self.engineer.create_spatial_features(
            self.coordinates, centroid=[0.0, 0.0]
        )
        expected = np.sqrt((self.coordinates**2).sum(axis=1))
        np.testing.assert_allclose(
            features["distance_from_centroid"].to_numpy(), expected
        )


class TestNormalizationTransformPaths:
    """fit_transform/transform honor the normalize contract."""

    @pytest.fixture
    def sample(self) -> tuple:
        np.random.seed(3)
        X = np.random.randn(20, 3)
        coords = np.random.randn(20, 2) * 10
        return X, coords

    def test_normalize_false_returns_raw_values(self, sample) -> None:
        X, coords = sample
        engineer = GeospatialFeatureEngineer(normalize=False)
        out = engineer.fit_transform(X, coordinates=coords)
        assert engineer.scaler is None
        # Non-normalized output must contain the untouched original features
        np.testing.assert_allclose(out[:, :3], X)

        X, coords = sample
        engineer = GeospatialFeatureEngineer(normalize=True)
        train_out = engineer.fit_transform(X, coordinates=coords)
        assert engineer.scaler is not None
        # Training output standardized: near-zero mean, near-unit variance
        train_mean = train_out[:, :3].mean(axis=0)
        assert np.all(np.abs(train_mean) < 1e-9)

        held_out = engineer.transform(X[:5], coordinates=coords[:5])
        assert held_out.shape[1] == train_out.shape[1]
        assert np.all(np.isfinite(held_out))

    def test_transform_with_fresh_coordinates_after_fit(self, sample) -> None:
        X, coords = sample
        engineer = GeospatialFeatureEngineer(normalize=False)
        engineer.fit_transform(X, coordinates=coords)
        fresh = np.random.RandomState(11).randn(4, 2) * 10
        out = engineer.transform(X[:4], coordinates=fresh)
        assert out.shape[0] == 4
        assert np.all(np.isfinite(out))


class TestTemporalAggregationFeatures:
    """create_temporal_aggregation_features rolling windows."""

    def test_rolling_windows_match_reference_series(self) -> None:
        timestamps = pd.date_range("2024-01-01", periods=10, freq="D")
        values = np.arange(10, dtype=float)
        engineer = GeospatialFeatureEngineer()
        features = engineer.create_temporal_aggregation_features(
            values, timestamps, window_sizes=[3, 5]
        )

        series = pd.Series(values)
        # min_periods=1 keeps the head rows finite
        expected_mean_3 = series.rolling(3, min_periods=1).mean().to_numpy()
        np.testing.assert_allclose(
            features["rolling_mean_3"].to_numpy(), expected_mean_3
        )
        assert features.shape[0] == 10
        assert list(features.columns) == [
            "rolling_mean_3",
            "rolling_std_3",
            "rolling_min_3",
            "rolling_max_3",
            "rolling_mean_5",
            "rolling_std_5",
            "rolling_min_5",
            "rolling_max_5",
        ]

    def test_unsorted_timestamps_restore_original_order(self) -> None:
        order = [3, 0, 4, 1, 2]
        times = pd.DatetimeIndex(pd.date_range("2024-01-01", periods=5, freq="D"))[
            order
        ]
        values = np.array([3.0, 0.0, 4.0, 1.0, 2.0])

        engineer = GeospatialFeatureEngineer()
        features = engineer.create_temporal_aggregation_features(
            values, times, window_sizes=[3]
        )
        # Output is unsorted back to the caller's row order; rolling stats
        # are computed over the time-sorted series [0,1,2,3,4].
        expected = np.array([2.0, 0.0, 3.0, 0.5, 1.0])
        np.testing.assert_allclose(
            features["rolling_mean_3"].to_numpy(), expected
        )
