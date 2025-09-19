"""
Unit tests for data preprocessing functionality
"""

import numpy as np
import pytest

from geo_infer_spm.models.data_models import SPMData
from geo_infer_spm.utils.preprocessing import (
    preprocess_data,
    handle_missing_data,
    normalize_data,
    remove_outliers,
    spatial_filter,
    temporal_filter
)


class TestDataPreprocessingPipeline:
    """Test complete preprocessing pipeline."""

    def setup_method(self):
        """Set up test data."""
        np.random.seed(42)
        n_points = 100

        self.coordinates = np.column_stack([
            np.random.uniform(-180, 180, n_points),
            np.random.uniform(-90, 90, n_points)
        ])

        # Create data with some structure
        self.data = (
            10 +  # baseline
            0.5 * self.coordinates[:, 0] / 180 +  # longitude effect
            0.3 * self.coordinates[:, 1] / 90 +   # latitude effect
            0.2 * np.random.randn(n_points)       # noise
        )

        self.spm_data = SPMData(
            data=self.data,
            coordinates=self.coordinates,
            crs='EPSG:4326'
        )

    def test_full_preprocessing_pipeline(self):
        """Test complete preprocessing pipeline."""
        processed = preprocess_data(
            self.spm_data,
            steps=['validate', 'normalize', 'remove_outliers'],
            normalize_params={'method': 'zscore'},
            outlier_params={'method': 'iqr', 'threshold': 1.5}
        )

        assert processed is not self.spm_data  # Should return new object
        assert 'preprocessing_steps' in processed.metadata
        assert 'preprocessing_params' in processed.metadata

    def test_selective_preprocessing(self):
        """Test selective preprocessing steps."""
        # Test only normalization
        processed = preprocess_data(self.spm_data, steps=['normalize'])

        assert processed.metadata['preprocessing_steps'] == ['normalize']

        # Test multiple steps
        processed = preprocess_data(
            self.spm_data,
            steps=['validate', 'normalize']
        )

        assert set(processed.metadata['preprocessing_steps']) == {'validate', 'normalize'}

    def test_invalid_preprocessing_step(self):
        """Test error handling for invalid preprocessing steps."""
        with pytest.warns(None) as warnings:
            processed = preprocess_data(self.spm_data, steps=['invalid_step'])

        # Should warn about invalid step but continue
        assert processed is not None
        assert len(warnings) >= 1


class TestMissingDataHandling:
    """Test missing data handling functionality."""

    def setup_method(self):
        """Set up test data with missing values."""
        np.random.seed(42)
        n_points = 50

        self.coordinates = np.random.rand(n_points, 2) * 100
        self.data = np.random.randn(n_points)

        # Introduce missing values
        missing_indices = np.random.choice(n_points, size=5, replace=False)
        self.data[missing_indices] = np.nan

        self.spm_data = SPMData(
            data=self.data,
            coordinates=self.coordinates,
            crs='EPSG:4326'
        )

    def test_missing_data_detection(self):
        """Test detection of missing data."""
        processed = handle_missing_data(self.spm_data, method='interpolate')

        # Should have no NaN values after processing
        assert not np.any(np.isnan(processed.data))
        assert processed.metadata['missing_data_handled']['method'] == 'interpolate'

    def test_drop_missing_method(self):
        """Test dropping missing data points."""
        original_n_points = len(self.spm_data.data)

        processed = handle_missing_data(self.spm_data, method='drop')

        # Should have fewer points
        assert len(processed.data) < original_n_points
        assert len(processed.coordinates) == len(processed.data)
        assert not np.any(np.isnan(processed.data))

    def test_mean_imputation(self):
        """Test mean imputation for missing data."""
        processed = handle_missing_data(self.spm_data, method='mean')

        # Should have same number of points
        assert len(processed.data) == len(self.spm_data.data)
        assert not np.any(np.isnan(processed.data))

        # Check that imputed values are reasonable
        assert np.all(np.isfinite(processed.data))

    def test_interpolation_method(self):
        """Test spatial interpolation of missing data."""
        processed = handle_missing_data(self.spm_data, method='interpolate')

        # Should have same number of points
        assert len(processed.data) == len(self.spm_data.data)
        assert not np.any(np.isnan(processed.data))

        # Coordinates should be unchanged
        np.testing.assert_array_equal(processed.coordinates, self.spm_data.coordinates)

    def test_too_many_missing_data(self):
        """Test handling of excessive missing data."""
        # Create data with too many missing values
        data_too_many_missing = self.data.copy()
        data_too_many_missing[:40] = np.nan  # 80% missing

        spm_data_missing = SPMData(
            data=data_too_many_missing,
            coordinates=self.coordinates,
            crs='EPSG:4326'
        )

        with pytest.raises(ValueError, match="Too much missing data"):
            handle_missing_data(spm_data_missing, method='interpolate', max_missing_fraction=0.5)


class TestDataNormalization:
    """Test data normalization functionality."""

    def setup_method(self):
        """Set up test data."""
        np.random.seed(42)
        n_points = 100

        self.coordinates = np.random.rand(n_points, 2) * 100
        self.data = np.random.normal(50, 10, n_points)  # Mean 50, std 10

        self.spm_data = SPMData(
            data=self.data,
            coordinates=self.coordinates,
            crs='EPSG:4326'
        )

    def test_zscore_normalization(self):
        """Test z-score normalization."""
        processed = normalize_data(self.spm_data, method='zscore')

        # Should have approximately zero mean and unit variance
        assert abs(np.mean(processed.data)) < 0.1
        assert abs(np.std(processed.data) - 1.0) < 0.1

        # Check metadata
        assert processed.metadata['normalization']['method'] == 'zscore'

    def test_minmax_normalization(self):
        """Test min-max normalization."""
        processed = normalize_data(self.spm_data, method='minmax')

        # Should be in [0, 1] range
        assert np.min(processed.data) >= 0.0
        assert np.max(processed.data) <= 1.0

        assert processed.metadata['normalization']['method'] == 'minmax'

    def test_robust_normalization(self):
        """Test robust normalization using median and MAD."""
        # Add some outliers
        data_with_outliers = self.data.copy()
        data_with_outliers[:5] = 200  # Add extreme outliers

        spm_data_outliers = SPMData(
            data=data_with_outliers,
            coordinates=self.coordinates,
            crs='EPSG:4326'
        )

        processed = normalize_data(spm_data_outliers, method='robust')

        # Robust normalization should be less affected by outliers
        assert np.all(np.isfinite(processed.data))
        assert processed.metadata['normalization']['method'] == 'robust'

    def test_invalid_normalization_method(self):
        """Test error handling for invalid normalization methods."""
        with pytest.raises(ValueError, match="Unknown normalization method"):
            normalize_data(self.spm_data, method='invalid')


class TestOutlierRemoval:
    """Test outlier removal functionality."""

    def setup_method(self):
        """Set up test data with outliers."""
        np.random.seed(42)
        n_points = 100

        self.coordinates = np.random.rand(n_points, 2) * 100
        self.data = np.random.normal(0, 1, n_points)

        # Add outliers
        outlier_indices = [10, 20, 30]
        self.data[outlier_indices] = [5.0, -5.0, 6.0]  # Extreme values

        self.spm_data = SPMData(
            data=self.data,
            coordinates=self.coordinates,
            crs='EPSG:4326'
        )

    def test_iqr_outlier_removal(self):
        """Test IQR-based outlier removal."""
        original_n_points = len(self.spm_data.data)

        processed = remove_outliers(self.spm_data, method='iqr', threshold=1.5)

        # Should have removed some points
        assert len(processed.data) <= original_n_points
        assert len(processed.coordinates) == len(processed.data)

        # Check metadata
        assert processed.metadata['outlier_removal']['method'] == 'iqr'
        assert 'n_outliers_removed' in processed.metadata['outlier_removal']

    def test_zscore_outlier_removal(self):
        """Test z-score based outlier removal."""
        processed = remove_outliers(self.spm_data, method='zscore', threshold=3.0)

        # Should remove extreme outliers
        assert len(processed.data) < len(self.spm_data.data)
        assert processed.metadata['outlier_removal']['method'] == 'zscore'

    def test_isolation_forest_outlier_removal(self):
        """Test isolation forest outlier removal."""
        try:
            processed = remove_outliers(self.spm_data, method='isolation_forest')

            assert processed.metadata['outlier_removal']['method'] == 'isolation_forest'
            assert len(processed.data) <= len(self.spm_data.data)

        except ImportError:
            pytest.skip("scikit-learn not available for isolation forest")

    def test_no_outliers(self):
        """Test outlier removal on data without outliers."""
        clean_data = np.random.normal(0, 1, 50)
        coordinates = np.random.rand(50, 2) * 100

        clean_spm_data = SPMData(data=clean_data, coordinates=coordinates, crs='EPSG:4326')

        processed = remove_outliers(clean_spm_data, method='iqr')

        # Should keep most or all points
        assert len(processed.data) >= len(clean_spm_data.data) * 0.9

    def test_invalid_outlier_method(self):
        """Test error handling for invalid outlier methods."""
        with pytest.raises(ValueError, match="Unknown outlier detection method"):
            remove_outliers(self.spm_data, method='invalid')


class TestSpatialFiltering:
    """Test spatial filtering functionality."""

    def setup_method(self):
        """Set up test data."""
        np.random.seed(42)
        n_points = 50

        self.coordinates = np.random.rand(n_points, 2) * 100
        self.data = np.sin(self.coordinates[:, 0] / 10) + 0.1 * np.random.randn(n_points)

        self.spm_data = SPMData(
            data=self.data,
            coordinates=self.coordinates,
            crs='EPSG:4326'
        )

    def test_gaussian_spatial_filter(self):
        """Test Gaussian spatial filtering."""
        processed = spatial_filter(self.spm_data, method='gaussian', sigma=5.0)

        # Should have same number of points
        assert len(processed.data) == len(self.spm_data.data)
        assert processed.metadata['spatial_filter']['method'] == 'gaussian'
        assert processed.metadata['spatial_filter']['sigma'] == 5.0

    def test_median_spatial_filter(self):
        """Test median spatial filtering."""
        processed = spatial_filter(self.spm_data, method='median', sigma=5.0)

        assert len(processed.data) == len(self.spm_data.data)
        assert processed.metadata['spatial_filter']['method'] == 'median'

    def test_mean_spatial_filter(self):
        """Test mean spatial filtering."""
        processed = spatial_filter(self.spm_data, method='mean', sigma=5.0)

        assert len(processed.data) == len(self.spm_data.data)
        assert processed.metadata['spatial_filter']['method'] == 'mean'


class TestTemporalFiltering:
    """Test temporal filtering functionality."""

    def setup_method(self):
        """Set up temporal test data."""
        np.random.seed(42)
        n_timepoints = 100

        self.time_points = np.arange(n_timepoints)
        self.data = (
            np.sin(2 * np.pi * self.time_points / 12) +  # Seasonal pattern
            0.01 * self.time_points +                    # Trend
            0.1 * np.random.randn(n_timepoints)         # Noise
        )

        self.coordinates = np.random.rand(1, 2) * 100  # Single spatial point
        self.spm_data = SPMData(
            data=self.data,
            coordinates=self.coordinates,
            time=self.time_points,
            crs='EPSG:4326'
        )

    def test_moving_average_filter(self):
        """Test moving average temporal filtering."""
        processed = temporal_filter(self.spm_data, method='moving_average', window_size=5)

        assert len(processed.data) == len(self.spm_data.data)
        assert processed.metadata['temporal_filter']['method'] == 'moving_average'
        assert processed.metadata['temporal_filter']['window_size'] == 5

    def test_exponential_filter(self):
        """Test exponential temporal filtering."""
        processed = temporal_filter(self.spm_data, method='exponential', window_size=10)

        assert len(processed.data) == len(self.spm_data.data)
        assert processed.metadata['temporal_filter']['method'] == 'exponential'

    def test_savgol_filter(self):
        """Test Savitzky-Golay filtering."""
        try:
            processed = temporal_filter(self.spm_data, method='savitzky_golay', window_size=7)

            assert len(processed.data) == len(self.spm_data.data)
            assert processed.metadata['temporal_filter']['method'] == 'savitzky_golay'

        except ImportError:
            pytest.skip("SciPy not available for Savitzky-Golay filter")

    def test_temporal_filter_without_time(self):
        """Test error handling when temporal data is missing."""
        spatial_only_data = SPMData(
            data=self.data,
            coordinates=self.coordinates,
            crs='EPSG:4326'
            # No time dimension
        )

        with pytest.raises(ValueError, match="Temporal filtering requires time dimension"):
            temporal_filter(spatial_only_data, method='moving_average')


class TestPreprocessingEdgeCases:
    """Test preprocessing edge cases and error conditions."""

    def test_empty_preprocessing_steps(self):
        """Test preprocessing with empty steps list."""
        coordinates = np.random.rand(10, 2) * 100
        data = np.random.randn(10)
        spm_data = SPMData(data=data, coordinates=coordinates, crs='EPSG:4326')

        processed = preprocess_data(spm_data, steps=[])

        # Should return unchanged data
        assert processed is spm_data

    def test_single_point_preprocessing(self):
        """Test preprocessing on single data point."""
        coordinates = np.array([[0.0, 0.0]])
        data = np.array([1.0])
        spm_data = SPMData(data=data, coordinates=coordinates, crs='EPSG:4326')

        processed = preprocess_data(spm_data, steps=['normalize'])

        assert len(processed.data) == 1
        assert processed.metadata['preprocessing_steps'] == ['normalize']

    def test_constant_data_normalization(self):
        """Test normalization of constant data."""
        coordinates = np.random.rand(10, 2) * 100
        data = np.full(10, 5.0)  # Constant value
        spm_data = SPMData(data=data, coordinates=coordinates, crs='EPSG:4326')

        # Should handle constant data gracefully
        processed = normalize_data(spm_data, method='zscore')

        # Result should be NaN or handled appropriately
        assert len(processed.data) == 10

    def test_extreme_outliers(self):
        """Test outlier removal with extreme values."""
        coordinates = np.random.rand(20, 2) * 100
        data = np.random.normal(0, 1, 20)
        data[10] = 1000  # Extreme outlier

        spm_data = SPMData(data=data, coordinates=coordinates, crs='EPSG:4326')

        processed = remove_outliers(spm_data, method='zscore', threshold=3.0)

        # Should remove the extreme outlier
        assert len(processed.data) < len(spm_data.data)

    def test_preprocessing_metadata_preservation(self):
        """Test that preprocessing preserves important metadata."""
        coordinates = np.random.rand(10, 2) * 100
        data = np.random.randn(10)

        original_metadata = {'source': 'test', 'quality_score': 0.95}
        spm_data = SPMData(
            data=data,
            coordinates=coordinates,
            crs='EPSG:4326',
            metadata=original_metadata
        )

        processed = preprocess_data(spm_data, steps=['normalize'])

        # Should preserve original metadata
        assert processed.metadata['source'] == 'test'
        assert processed.metadata['quality_score'] == 0.95

        # Should add preprocessing metadata
        assert 'preprocessing_steps' in processed.metadata
        assert 'preprocessing_params' in processed.metadata
