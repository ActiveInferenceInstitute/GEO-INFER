"""
Unit tests for Random Field Theory functionality
"""

import numpy as np
import pytest

from geo_infer_spm.core.rft import RandomFieldTheory, compute_spm
from geo_infer_spm.models.data_models import SPMData, SPMResult, ContrastResult, DesignMatrix


class TestRandomFieldTheory:
    """Test RandomFieldTheory class functionality."""

    def setup_method(self):
        """Set up test data."""
        self.field_shape = (10, 10)  # 2D field
        self.rft = RandomFieldTheory(self.field_shape)

    def test_initialization(self):
        """Test RFT initialization."""
        assert self.rft.field_shape == (10, 10)
        assert self.rft.ndim == 2
        assert self.rft.smoothness is None
        assert self.rft.search_volume is None

        # Check RFT constants for different dimensions
        assert 2 in self.rft._rft_constants
        assert 3 in self.rft._rft_constants

    def test_smoothness_estimation(self):
        """Test field smoothness estimation."""
        # Create synthetic smooth field
        x, y = np.meshgrid(np.arange(10), np.arange(10))
        # Add some smooth variation
        smooth_field = np.sin(0.5 * x) * np.cos(0.3 * y) + 0.1 * np.random.randn(10, 10)

        residuals = smooth_field.flatten()
        smoothness = self.rft.estimate_smoothness(residuals)

        assert isinstance(smoothness, np.ndarray)
        assert len(smoothness) == 2  # 2D field
        assert np.all(smoothness > 0)  # Should be positive

    def test_search_volume_computation(self):
        """Test search volume computation."""
        # Set smoothness first
        self.rft.smoothness = np.array([2.0, 2.0])  # FWHM in each dimension

        voxel_sizes = np.array([1.0, 1.0])  # Unit voxels
        search_volume = self.rft.compute_search_volume(voxel_sizes)

        assert isinstance(search_volume, float)
        assert search_volume > 0
        assert self.rft.search_volume == search_volume

    def test_expected_clusters_computation(self):
        """Test expected clusters computation."""
        # Set up RFT parameters
        self.rft.smoothness = np.array([2.0, 2.0])
        self.rft.search_volume = 100.0

        threshold = 2.0
        expected_k = self.rft.expected_clusters(threshold, stat_type='Z')

        assert isinstance(expected_k, float)
        assert expected_k >= 0

        # Higher threshold should give fewer expected clusters
        expected_k_higher = self.rft.expected_clusters(3.0, stat_type='Z')
        assert expected_k_higher < expected_k

    def test_cluster_threshold_computation(self):
        """Test cluster-forming threshold computation."""
        self.rft.smoothness = np.array([2.0, 2.0])
        self.rft.search_volume = 50.0

        alpha = 0.05
        threshold = self.rft.cluster_threshold(alpha, stat_type='Z')

        assert isinstance(threshold, float)
        assert threshold > 0

        # Lower alpha should give higher threshold
        threshold_strict = self.rft.cluster_threshold(0.01, stat_type='Z')
        assert threshold_strict > threshold

    def test_peak_threshold_computation(self):
        """Test peak-level threshold computation."""
        self.rft.search_volume = 100.0

        alpha = 0.05
        threshold = self.rft.peak_threshold(alpha, stat_type='Z')

        assert isinstance(threshold, float)
        assert threshold > 0

    def test_p_value_correction(self):
        """Test p-value correction using RFT."""
        # Create mock statistical map
        stat_map = np.random.randn(100)

        # Set up RFT parameters
        rft = RandomFieldTheory((10, 10))
        rft.smoothness = np.array([1.5, 1.5])
        rft.search_volume = 25.0

        corrected_p = rft.correct_p_values(stat_map, stat_type='Z', method='cluster')

        assert corrected_p.shape == stat_map.shape
        assert np.all((corrected_p >= 0) & (corrected_p <= 1))
        assert np.all(corrected_p >= stat_map)  # Corrected p-values should be >= uncorrected


class TestRFTDifferentDimensions:
    """Test RFT with different field dimensions."""

    def test_1d_field(self):
        """Test 1D field RFT."""
        rft_1d = RandomFieldTheory((50,))  # 1D field

        assert rft_1d.ndim == 1
        assert rft_1d.field_shape == (50,)

        # Test smoothness estimation
        data_1d = np.sin(np.linspace(0, 4*np.pi, 50)) + 0.1 * np.random.randn(50)
        smoothness = rft_1d.estimate_smoothness(data_1d)

        assert len(smoothness) == 1
        assert smoothness[0] > 0

    def test_3d_field(self):
        """Test 3D field RFT."""
        rft_3d = RandomFieldTheory((5, 5, 5))  # 3D field

        assert rft_3d.ndim == 3
        assert rft_3d.field_shape == (5, 5, 5)

        # Should have 3D RFT constants
        assert 3 in rft_3d._rft_constants


class TestComputeSPM:
    """Test the compute_spm function."""

    def setup_method(self):
        """Set up test data."""
        np.random.seed(42)
        n_points = 50

        # Create mock SPM result
        coordinates = np.random.rand(n_points, 2) * 100
        X = np.random.randn(n_points, 3)
        beta = np.array([1.0, 2.0, -1.0])
        y = X @ beta + 0.1 * np.random.randn(n_points)

        spm_data = SPMData(data=y, coordinates=coordinates, crs='EPSG:4326')
        design_matrix = DesignMatrix(matrix=X, names=['int', 'x1', 'x2'])

        self.spm_result = SPMResult(
            spm_data=spm_data,
            design_matrix=design_matrix,
            beta_coefficients=beta,
            residuals=y - X @ beta,
            model_diagnostics={'r_squared': 0.95}
        )

    def test_compute_spm_rft(self):
        """Test SPM computation with RFT correction."""
        # Create contrast
        contrast_vector = np.array([0, 1, 0])  # Test x1 coefficient
        contrast_result = ContrastResult(
            contrast_vector=contrast_vector,
            t_statistic=np.random.randn(50),  # Mock t-statistics
            effect_size=np.random.randn(50),
            standard_error=np.ones(50),
            p_values=np.random.rand(50)
        )

        # Compute SPM with RFT
        corrected_result = compute_spm(self.spm_result, contrast_result, correction='RFT')

        assert hasattr(corrected_result, 'corrected_p_values')
        assert corrected_result.correction_method == 'RFT'
        assert corrected_result.corrected_p_values.shape == contrast_result.p_values.shape

    def test_compute_spm_fdr(self):
        """Test SPM computation with FDR correction."""
        contrast_result = ContrastResult(
            contrast_vector=np.array([0, 1, 0]),
            t_statistic=np.random.randn(50),
            effect_size=np.random.randn(50),
            standard_error=np.ones(50),
            p_values=np.random.rand(50) * 0.1  # Some significant p-values
        )

        corrected_result = compute_spm(self.spm_result, contrast_result, correction='FDR')

        assert corrected_result.correction_method == 'FDR'
        assert corrected_result.corrected_p_values.shape == contrast_result.p_values.shape

    def test_compute_spm_bonferroni(self):
        """Test SPM computation with Bonferroni correction."""
        contrast_result = ContrastResult(
            contrast_vector=np.array([0, 1, 0]),
            t_statistic=np.random.randn(50),
            effect_size=np.random.randn(50),
            standard_error=np.ones(50),
            p_values=np.random.rand(50)
        )

        corrected_result = compute_spm(self.spm_result, contrast_result, correction='Bonferroni')

        assert corrected_result.correction_method == 'Bonferroni'
        # Bonferroni correction should be more conservative
        assert np.all(corrected_result.corrected_p_values >= contrast_result.p_values)

    def test_compute_spm_uncorrected(self):
        """Test SPM computation without correction."""
        contrast_result = ContrastResult(
            contrast_vector=np.array([0, 1, 0]),
            t_statistic=np.random.randn(50),
            effect_size=np.random.randn(50),
            standard_error=np.ones(50),
            p_values=np.random.rand(50)
        )

        corrected_result = compute_spm(self.spm_result, contrast_result, correction='uncorrected')

        assert corrected_result.correction_method == 'uncorrected'
        np.testing.assert_array_equal(corrected_result.corrected_p_values, contrast_result.p_values)


class TestRFTStatisticalTests:
    """Test statistical correctness of RFT methods."""

    def test_z_to_t_conversion(self):
        """Test conversion between Z and t statistics."""
        rft = RandomFieldTheory((20, 20))
        rft.search_volume = 50.0

        df = 30  # Degrees of freedom

        # Same threshold should give different results for Z vs t
        threshold = 2.0
        expected_z = rft.expected_clusters(threshold, stat_type='Z')
        expected_t = rft.expected_clusters(threshold, stat_type='t')

        # For same numerical threshold, Z and t should give different results
        # (since t is less extreme than Z for same value)
        assert expected_t != expected_z

    def test_monotonicity(self):
        """Test that RFT functions are monotonic."""
        rft = RandomFieldTheory((15, 15))
        rft.smoothness = np.array([2.0, 2.0])
        rft.search_volume = 40.0

        thresholds = [1.5, 2.0, 2.5, 3.0]
        expected_clusters = [rft.expected_clusters(t, stat_type='Z') for t in thresholds]

        # Higher thresholds should give fewer expected clusters
        assert expected_clusters[0] > expected_clusters[1] > expected_clusters[2] > expected_clusters[3]

    def test_field_size_effect(self):
        """Test effect of field size on RFT results."""
        # Small field
        rft_small = RandomFieldTheory((5, 5))
        rft_small.smoothness = np.array([1.0, 1.0])
        rft_small.search_volume = 10.0

        # Large field
        rft_large = RandomFieldTheory((15, 15))
        rft_large.smoothness = np.array([1.0, 1.0])
        rft_large.search_volume = 90.0

        threshold = 2.0
        expected_small = rft_small.expected_clusters(threshold, stat_type='Z')
        expected_large = rft_large.expected_clusters(threshold, stat_type='Z')

        # Larger field should have more expected clusters
        assert expected_large > expected_small


class TestRFTEdgeCases:
    """Test RFT edge cases and error conditions."""

    def test_invalid_dimensions(self):
        """Test error handling for invalid field dimensions."""
        with pytest.raises(ValueError, match="RFT supports 1D, 2D, and 3D fields"):
            RandomFieldTheory((10, 10, 10, 10))  # 4D field

    def test_missing_smoothness(self):
        """Test error when smoothness not estimated."""
        rft = RandomFieldTheory((10, 10))

        with pytest.raises(ValueError, match="Smoothness must be estimated"):
            rft.compute_search_volume()

    def test_missing_search_volume(self):
        """Test error when search volume not computed."""
        rft = RandomFieldTheory((10, 10))

        with pytest.raises(ValueError, match="Search volume must be computed"):
            rft.expected_clusters(2.0)

    def test_zero_smoothness(self):
        """Test handling of zero smoothness (should use default)."""
        rft = RandomFieldTheory((10, 10))

        # Create residuals with no spatial variation
        residuals = np.random.randn(100)  # No spatial structure

        smoothness = rft.estimate_smoothness(residuals)

        # Should still produce valid smoothness estimates
        assert np.all(smoothness > 0)
        assert len(smoothness) == 2

    def test_extreme_thresholds(self):
        """Test RFT with extreme statistical thresholds."""
        rft = RandomFieldTheory((8, 8))
        rft.smoothness = np.array([1.0, 1.0])
        rft.search_volume = 20.0

        # Very liberal threshold
        expected_liberal = rft.expected_clusters(0.5, stat_type='Z')

        # Very conservative threshold
        expected_conservative = rft.expected_clusters(4.0, stat_type='Z')

        assert expected_liberal > expected_conservative

        # Very conservative should be close to zero
        assert expected_conservative < 0.01

    def test_cluster_detection_empty_field(self):
        """Test cluster detection on uniform field."""
        from geo_infer_spm.core.spatial_analysis import SpatialAnalyzer

        coordinates = np.random.rand(25, 2) * 50
        analyzer = SpatialAnalyzer(coordinates)

        # Uniform statistical field (no clusters)
        stat_map = np.ones(25) * 0.5  # Below any reasonable threshold

        clusters = analyzer.detect_clusters(stat_map, threshold=2.0)

        assert clusters['n_clusters'] == 0
        assert len(clusters['clusters']) == 0
