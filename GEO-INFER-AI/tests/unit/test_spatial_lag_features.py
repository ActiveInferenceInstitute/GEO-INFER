"""
Unit tests for spatial lag and distance features in feature engineering.
"""

import numpy as np
import pandas as pd
import pytest

from geo_infer_ai.preprocessing.feature_engineering import GeospatialFeatureEngineer


class TestSpatialLagFeatures:
    """Test spatial lag feature creation."""

    @pytest.fixture
    def engineer(self) -> GeospatialFeatureEngineer:
        return GeospatialFeatureEngineer(normalize=False)

    @pytest.fixture
    def spatial_data(self) -> tuple:
        np.random.seed(42)
        coords = np.array([
            [0.0, 0.0], [1.0, 0.0], [0.0, 1.0],
            [1.0, 1.0], [0.5, 0.5],
        ])
        values = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        return coords, values

    def test_spatial_lag_shape(self, engineer: GeospatialFeatureEngineer, spatial_data: tuple) -> None:
        coords, values = spatial_data
        result = engineer.create_spatial_lag_features(values, coords, k_neighbors=2)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 5
        assert 'spatial_lag_v0_mean' in result.columns
        assert 'spatial_lag_v0_std' in result.columns

    def test_spatial_lag_multivariate(self, engineer: GeospatialFeatureEngineer) -> None:
        np.random.seed(42)
        coords = np.random.randn(10, 2)
        values = np.random.randn(10, 3)

        result = engineer.create_spatial_lag_features(values, coords, k_neighbors=3)

        # Should have mean and std for each of 3 variables
        assert 'spatial_lag_v0_mean' in result.columns
        assert 'spatial_lag_v1_mean' in result.columns
        assert 'spatial_lag_v2_mean' in result.columns
        assert len(result) == 10

    def test_spatial_lag_center_point(self, engineer: GeospatialFeatureEngineer) -> None:
        """Center point should have lag influenced by all neighbors."""
        coords = np.array([
            [-1.0, 0.0], [1.0, 0.0], [0.0, -1.0],
            [0.0, 1.0], [0.0, 0.0],
        ])
        values = np.array([10.0, 10.0, 10.0, 10.0, 0.0])

        result = engineer.create_spatial_lag_features(values, coords, k_neighbors=4)

        # Center point's lag should be close to 10 (all neighbors are 10)
        center_lag = result['spatial_lag_v0_mean'].iloc[4]
        assert center_lag > 5.0


class TestDistanceFeatures:
    """Test distance feature creation."""

    @pytest.fixture
    def engineer(self) -> GeospatialFeatureEngineer:
        return GeospatialFeatureEngineer(normalize=False)

    def test_distance_features_shape(self, engineer: GeospatialFeatureEngineer) -> None:
        coords = np.array([[0.0, 0.0], [1.0, 1.0], [2.0, 2.0]])
        refs = np.array([[0.0, 0.0], [5.0, 5.0]])
        ref_names = ['origin', 'far_point']

        result = engineer.create_distance_features(coords, refs, ref_names)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert 'dist_to_origin' in result.columns
        assert 'dist_to_far_point' in result.columns
        assert 'log_dist_to_origin' in result.columns

    def test_distance_to_self_is_zero(self, engineer: GeospatialFeatureEngineer) -> None:
        coords = np.array([[0.0, 0.0], [3.0, 4.0]])
        refs = np.array([[0.0, 0.0]])

        result = engineer.create_distance_features(coords, refs)

        assert result['dist_to_ref_0'].iloc[0] == 0.0
        assert abs(result['dist_to_ref_0'].iloc[1] - 5.0) < 1e-6  # 3-4-5 triangle

    def test_distance_symmetry(self, engineer: GeospatialFeatureEngineer) -> None:
        """Distance from A to B should equal distance from B to A."""
        coords = np.array([[1.0, 2.0], [4.0, 6.0]])
        refs = np.array([[4.0, 6.0], [1.0, 2.0]])

        result = engineer.create_distance_features(coords, refs)

        dist_a_to_b = result['dist_to_ref_0'].iloc[0]
        dist_b_to_a = result['dist_to_ref_1'].iloc[1]
        np.testing.assert_allclose(dist_a_to_b, dist_b_to_a, atol=1e-10)


class TestTemporalAggregation:
    """Test temporal aggregation features."""

    @pytest.fixture
    def engineer(self) -> GeospatialFeatureEngineer:
        return GeospatialFeatureEngineer(normalize=False)

    def test_temporal_aggregation_shape(self, engineer: GeospatialFeatureEngineer) -> None:
        values = np.arange(20, dtype=float)
        timestamps = pd.date_range('2024-01-01', periods=20, freq='D')

        result = engineer.create_temporal_aggregation_features(
            values, timestamps, window_sizes=[3, 7]
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 20
        assert 'rolling_mean_3' in result.columns
        assert 'rolling_std_3' in result.columns
        assert 'rolling_mean_7' in result.columns

    def test_temporal_aggregation_rolling_mean(self, engineer: GeospatialFeatureEngineer) -> None:
        values = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        timestamps = pd.date_range('2024-01-01', periods=5, freq='D')

        result = engineer.create_temporal_aggregation_features(
            values, timestamps, window_sizes=[3]
        )

        # Rolling mean of last 3: [1.0, 1.5, 2.0, 3.0, 4.0]
        expected_last = np.mean([3.0, 4.0, 5.0])
        assert abs(result['rolling_mean_3'].iloc[4] - expected_last) < 1e-6
