"""
Unit tests for spatial analysis functionality
"""

import numpy as np
import pytest
from scipy.spatial.distance import pdist

from geo_infer_spm.models.data_models import SPMData
from geo_infer_spm.core.spatial_analysis import SpatialAnalyzer


class TestSpatialAnalyzer:
    """Test SpatialAnalyzer class functionality."""

    def setup_method(self):
        """Set up test data."""
        np.random.seed(42)
        n_points = 100

        # Create test coordinates and data
        self.coordinates = np.random.rand(n_points, 2) * 100
        self.data = np.random.randn(n_points)

        # Create SPMData
        self.spm_data = SPMData(
            data=self.data,
            coordinates=self.coordinates,
            crs='EPSG:4326'  # Use generic CRS to avoid lat/lon validation
        )

        self.analyzer = SpatialAnalyzer(self.coordinates)

    def test_initialization(self):
        """Test SpatialAnalyzer initialization."""
        assert self.analyzer.coordinates.shape == (100, 2)
        assert self.analyzer.distance_matrix.shape == (100, 100)
        assert np.allclose(self.analyzer.distance_matrix.diagonal(), 0)

    def test_variogram_estimation(self):
        """Test empirical variogram estimation."""
        # Create spatially autocorrelated residuals
        distances = self.analyzer.distance_matrix
        residuals = self.data * np.exp(-distances / 50) + 0.1 * np.random.randn(100)

        variogram = self.analyzer.estimate_variogram(residuals, n_bins=10)

        assert 'distances' in variogram
        assert 'variogram' in variogram
        assert 'counts' in variogram
        assert 'model' in variogram
        assert len(variogram['distances']) == 10
        assert len(variogram['variogram']) == 10

        # Check that variogram increases with distance (spatial dependence)
        assert variogram['variogram'][-1] >= variogram['variogram'][0]

    def test_spatial_weights_creation(self):
        """Test spatial weights matrix creation."""
        # Estimate variogram first
        variogram = self.analyzer.estimate_variogram(self.data)

        # Create weights
        weights = self.analyzer.create_spatial_weights()

        assert weights.shape == (100, 100)
        assert np.allclose(weights.diagonal(), 1.0)  # Self-weights should be 1
        assert np.all(weights >= 0)  # Weights should be non-negative

    def test_cluster_detection(self):
        """Test significant cluster detection."""
        # Create synthetic statistical map with clusters
        stat_map = np.random.randn(100)

        # Add significant clusters
        cluster1_indices = np.arange(10, 20)
        cluster2_indices = np.arange(50, 60)
        stat_map[cluster1_indices] = 3.0 + np.random.randn(10)  # Significant cluster
        stat_map[cluster2_indices] = 2.5 + np.random.randn(10)  # Another significant cluster

        clusters = self.analyzer.detect_clusters(stat_map, threshold=2.0, min_cluster_size=5)

        assert 'n_clusters' in clusters
        assert 'clusters' in clusters
        assert clusters['n_clusters'] >= 2  # Should detect at least 2 clusters

        # Check cluster properties
        for cluster in clusters['clusters']:
            assert 'size' in cluster
            assert 'max_statistic' in cluster
            assert 'center_of_mass' in cluster
            assert cluster['size'] >= 5

    def test_geographically_weighted_regression(self):
        """Test GWR implementation."""
        # Create test data with spatial structure
        x_coord = self.coordinates[:, 0]
        y_coord = self.coordinates[:, 1]

        # Response variable with spatial trend
        response = 2.0 + 0.5 * x_coord + 0.3 * y_coord + 0.1 * np.random.randn(100)

        test_data = SPMData(
            data=response,
            coordinates=self.coordinates,
            covariates={'x': x_coord, 'y': y_coord}
        )

        result = self.analyzer.geographically_weighted_regression(test_data, bandwidth=20.0)

        assert result is not None
        assert hasattr(result, 'beta_coefficients')
        assert result.beta_coefficients.shape[1] > 0  # Should have coefficients

    def test_spatial_basis_functions(self):
        """Test spatial basis function generation."""
        # Test Gaussian basis functions
        gaussian_basis = self.analyzer.spatial_basis_functions(n_basis=5, method='gaussian')
        assert gaussian_basis.shape == (100, 5)
        assert np.all(gaussian_basis >= 0)  # Gaussian basis should be non-negative

        # Test polynomial basis functions
        poly_basis = self.analyzer.spatial_basis_functions(n_basis=3, method='polynomial')
        assert poly_basis.shape == (100, 3)

        # Test Fourier basis functions
        fourier_basis = self.analyzer.spatial_basis_functions(n_basis=6, method='fourier')
        assert fourier_basis.shape == (100, 6)

    def test_invalid_method(self):
        """Test error handling for invalid methods."""
        with pytest.raises(ValueError, match="Unknown basis method"):
            self.analyzer.spatial_basis_functions(method='invalid')


class TestSpatialAnalysisEdgeCases:
    """Test edge cases in spatial analysis."""

    def test_single_point(self):
        """Test behavior with single data point."""
        coordinates = np.array([[0.0, 0.0]])
        analyzer = SpatialAnalyzer(coordinates)

        assert analyzer.distance_matrix.shape == (1, 1)
        assert analyzer.distance_matrix[0, 0] == 0

    def test_collinear_points(self):
        """Test with collinear spatial points."""
        coordinates = np.array([[i, 0.0] for i in range(10)])
        analyzer = SpatialAnalyzer(coordinates)

        # Variogram should still work
        data = np.random.randn(10)
        variogram = analyzer.estimate_variogram(data, n_bins=5)
        assert len(variogram['variogram']) == 5

    def test_large_distance_matrix(self):
        """Test with larger coordinate set."""
        np.random.seed(42)
        coordinates = np.random.rand(50, 2) * 1000  # Larger area
        analyzer = SpatialAnalyzer(coordinates)

        assert analyzer.distance_matrix.shape == (50, 50)

        # Should handle large matrices
        data = np.random.randn(50)
        variogram = analyzer.estimate_variogram(data)
        assert 'model' in variogram


class TestSpatialWeights:
    """Test spatial weights functionality."""

    def test_exponential_weights(self):
        """Test exponential decay spatial weights."""
        coordinates = np.array([[0, 0], [1, 0], [0, 1], [1, 1]])
        analyzer = SpatialAnalyzer(coordinates)

        # Create mock variogram model
        analyzer.variogram_model = {
            'nugget': 0.0,
            'sill': 1.0,
            'range': 2.0,
            'model': 'exponential'
        }

        weights = analyzer.create_spatial_weights(model_type='exponential')
        assert weights.shape == (4, 4)
        assert np.allclose(weights.diagonal(), 1.0)

        # Check that closer points have higher weights
        assert weights[0, 1] > weights[0, 3]  # Point 1 is closer to 0 than point 3

    def test_gaussian_weights(self):
        """Test Gaussian spatial weights."""
        coordinates = np.array([[0, 0], [1, 0], [2, 0]])
        analyzer = SpatialAnalyzer(coordinates)

        analyzer.variogram_model = {
            'nugget': 0.1,
            'sill': 1.0,
            'range': 1.0,
            'model': 'gaussian'
        }

        weights = analyzer.create_spatial_weights(model_type='gaussian')
        assert weights.shape == (3, 3)

        # Gaussian weights should decay faster than exponential
        exp_weights = analyzer.create_spatial_weights(model_type='exponential')
        assert weights[0, 2] < exp_weights[0, 2]  # Gaussian decays faster

    def test_spherical_weights(self):
        """Test spherical variogram weights."""
        coordinates = np.random.rand(20, 2) * 10
        analyzer = SpatialAnalyzer(coordinates)

        analyzer.variogram_model = {
            'nugget': 0.0,
            'sill': 1.0,
            'range': 5.0,
            'model': 'spherical'
        }

        weights = analyzer.create_spatial_weights(model_type='spherical')
        assert weights.shape == (20, 20)
        assert np.all(weights <= 1.0)  # Spherical model max correlation is 1
        assert np.all(weights >= 0.0)


class TestClusterAnalysis:
    """Test cluster analysis functionality."""

    def test_no_clusters(self):
        """Test when no clusters meet threshold."""
        coordinates = np.random.rand(50, 2) * 100
        analyzer = SpatialAnalyzer(coordinates)

        # Random data below threshold
        stat_map = np.random.randn(50) * 0.5  # Low values

        clusters = analyzer.detect_clusters(stat_map, threshold=2.0)

        assert clusters['n_clusters'] == 0
        assert len(clusters['clusters']) == 0

    def test_single_large_cluster(self):
        """Test detection of single large cluster."""
        coordinates = np.random.rand(100, 2) * 100
        analyzer = SpatialAnalyzer(coordinates)

        stat_map = np.random.randn(100)
        # Make first 30 points significant
        stat_map[:30] = 3.0 + np.random.randn(30)

        clusters = analyzer.detect_clusters(stat_map, threshold=2.0, min_cluster_size=10)

        assert clusters['n_clusters'] >= 1

        # Largest cluster should contain most significant points
        largest_cluster = max(clusters['clusters'], key=lambda x: x['size'])
        assert largest_cluster['size'] >= 20

    def test_multiple_clusters(self):
        """Test detection of multiple distinct clusters."""
        # Create coordinates in three distinct groups
        coords1 = np.random.rand(20, 2) * 10
        coords2 = np.random.rand(20, 2) * 10 + np.array([50, 0])
        coords3 = np.random.rand(20, 2) * 10 + np.array([0, 50])
        coordinates = np.vstack([coords1, coords2, coords3])

        analyzer = SpatialAnalyzer(coordinates)

        stat_map = np.random.randn(60)
        # Make each group significant
        stat_map[:20] = 3.0 + np.random.randn(20)
        stat_map[20:40] = 2.8 + np.random.randn(20)
        stat_map[40:60] = 3.2 + np.random.randn(20)

        clusters = analyzer.detect_clusters(stat_map, threshold=2.0, min_cluster_size=5)

        assert clusters['n_clusters'] >= 2  # Should detect at least 2 clusters
