"""
Tests for the linalg_tensor module.
"""

import numpy as np
import pytest
from geo_infer_math.core.linalg_tensor import (
    TensorData, MatrixOperations, TensorOperations, SpatialLinearAlgebra
)

class TestMatrixOperations:
    """Test matrix operations functionality."""

    def test_condition_number(self):
        """Test condition number calculation."""
        # Well-conditioned matrix
        well_conditioned = np.eye(3)
        cond = MatrixOperations.condition_number(well_conditioned)
        assert cond == 1.0

        # Ill-conditioned matrix
        ill_conditioned = np.array([[1, 1], [1, 1.0001]])
        cond = MatrixOperations.condition_number(ill_conditioned)
        assert cond > 1.0

    def test_positive_definite_check(self):
        """Test positive definite matrix detection."""
        # Positive definite matrix
        pd_matrix = np.array([[2, -1], [-1, 2]])
        assert MatrixOperations.is_positive_definite(pd_matrix)

        # Negative definite matrix
        nd_matrix = -pd_matrix
        assert not MatrixOperations.is_positive_definite(nd_matrix)

        # Indefinite matrix
        indefinite = np.array([[1, 2], [2, -1]])
        assert not MatrixOperations.is_positive_definite(indefinite)

    def test_nearest_positive_definite(self):
        """Test finding nearest positive definite matrix."""
        # Start with indefinite matrix
        indefinite = np.array([[1, 2], [2, -1]])
        pd_matrix = MatrixOperations.nearest_positive_definite(indefinite)

        assert MatrixOperations.is_positive_definite(pd_matrix)

        # Check that it's close to original
        assert np.allclose(indefinite, pd_matrix, atol=0.1)

    def test_spatial_weights_matrix(self):
        """Test spatial weights matrix creation."""
        # Create simple coordinate data
        coords = np.array([
            [0, 0], [1, 0], [0, 1], [1, 1]
        ])

        # Test inverse distance weights
        weights = MatrixOperations.spatial_weights_matrix(
            coords, method='inverse_distance', k=3
        )

        assert weights.shape == (4, 4)
        assert np.allclose(weights, weights.T)  # Should be symmetric
        assert np.all(np.diag(weights) == 0)  # No self-weights

        # Test k-nearest neighbors
        weights_knn = MatrixOperations.spatial_weights_matrix(
            coords, method='knn', k=2
        )

        assert weights_knn.shape == (4, 4)
        assert np.allclose(weights_knn, weights_knn.T)

        # Test binary weights
        weights_binary = MatrixOperations.spatial_weights_matrix(
            coords, method='binary', threshold=1.5
        )

        assert weights_binary.shape == (4, 4)
        assert np.all(np.isin(weights_binary, [0, 1]))

    def test_moran_i_calculation(self):
        """Test Moran's I calculation using matrix operations."""
        # Create synthetic spatial data with clustering
        n = 10
        coords = np.random.rand(n, 2) * 10
        values = np.random.rand(n)

        # Create weights matrix
        weights = MatrixOperations.spatial_weights_matrix(coords, k=3)

        # Calculate Moran's I
        result = MatrixOperations.moran_i_matrix(values, weights)

        assert 'I' in result
        assert 'expected_I' in result
        assert 'variance' in result
        assert 'z_score' in result
        assert 'p_value' in result

        assert -1 <= result['I'] <= 1  # Moran's I should be in [-1, 1]
        assert 0 <= result['p_value'] <= 1

class TestTensorData:
    """Test TensorData class."""

    def test_tensor_data_creation(self):
        """Test creating TensorData objects."""
        data = np.random.rand(5, 10, 20)
        tensor = TensorData(
            data=data,
            dimensions=['time', 'lat', 'lon'],
            metadata={'units': 'meters'}
        )

        assert tensor.data.shape == (5, 10, 20)
        assert tensor.dimensions == ['time', 'lat', 'lon']
        assert tensor.metadata['units'] == 'meters'

    def test_tensor_data_default_dimensions(self):
        """Test default dimension naming."""
        data = np.random.rand(3, 4, 5)
        tensor = TensorData(data=data)

        assert tensor.dimensions == ['dim_0', 'dim_1', 'dim_2']

class TestTensorOperations:
    """Test tensor operations functionality."""

    def setup_method(self):
        """Set up test tensor data."""
        # Create spatiotemporal tensor (time, lat, lon)
        self.spatial_data = [
            np.random.rand(10, 20) for _ in range(5)
        ]
        self.temporal_indices = [0, 1, 2, 3, 4]
        self.spatial_coords = np.random.rand(10, 20, 2)

        self.tensor = TensorOperations.create_spatiotemporal_tensor(
            self.spatial_data, self.temporal_indices, self.spatial_coords
        )

    def test_tensor_creation(self):
        """Test spatiotemporal tensor creation."""
        assert self.tensor.data.shape == (5, 10, 20)
        assert self.tensor.dimensions == ['time', 'latitude', 'longitude']
        assert self.tensor.metadata['n_time_steps'] == 5

    def test_tensor_unfold(self):
        """Test tensor unfolding."""
        # Unfold along time mode
        unfolded, shape_info = TensorOperations.tensor_unfold(self.tensor, mode=0)

        assert unfolded.shape == (10 * 20, 5)
        assert shape_info['mode'] == 0

        # Unfold along spatial modes
        unfolded_lat, shape_info_lat = TensorOperations.tensor_unfold(self.tensor, mode=1)
        assert unfolded_lat.shape == (10, 5 * 20)
        assert shape_info_lat['mode'] == 1

    def test_tensor_fold(self):
        """Test tensor folding."""
        # Unfold and then fold back
        unfolded, shape_info = TensorOperations.tensor_unfold(self.tensor, mode=0)
        folded = TensorOperations.tensor_fold(unfolded, shape_info)

        assert folded.shape == self.tensor.data.shape
        np.testing.assert_array_almost_equal(folded, self.tensor.data)

    def test_principal_component_analysis(self):
        """Test PCA on tensor data."""
        pca_result = TensorOperations.principal_component_analysis(self.tensor)

        assert 'principal_components' in pca_result
        assert 'explained_variance' in pca_result
        assert 'cumulative_variance' in pca_result
        assert 'eigenvalues' in pca_result
        assert 'singular_values' in pca_result

        # Check that explained variance sums to reasonable values
        assert np.sum(pca_result['explained_variance']) <= 1.1  # Allow for numerical precision

    def test_tensor_decomposition_cp(self):
        """Test CP tensor decomposition."""
        rank = 3
        cp_result = TensorOperations.tensor_decomposition(self.tensor, rank, method='cp')

        assert 'factor_matrices' in cp_result
        assert 'rank' in cp_result
        assert len(cp_result['factor_matrices']) == 3  # One for each mode
        assert cp_result['rank'] == rank

    def test_tensor_decomposition_tucker(self):
        """Test Tucker tensor decomposition."""
        rank = 2
        tucker_result = TensorOperations.tensor_decomposition(self.tensor, rank, method='tucker')

        assert 'core_tensor' in tucker_result
        assert 'factor_matrices' in tucker_result
        assert 'rank' in tucker_result
        assert tucker_result['core_tensor'].shape == (rank, rank, rank)

    def test_invalid_decomposition_method(self):
        """Test handling of invalid decomposition method."""
        with pytest.raises(ValueError):
            TensorOperations.tensor_decomposition(self.tensor, 2, method='invalid')

class TestSpatialLinearAlgebra:
    """Test spatial linear algebra functionality."""

    def setup_method(self):
        """Set up test data."""
        np.random.seed(42)
        self.n_samples = 50
        self.n_features = 3

        self.X = np.random.randn(self.n_samples, self.n_features)
        self.y = self.X @ np.array([1, 2, -1]) + 0.1 * np.random.randn(self.n_samples)

        # Create coordinates
        self.coords = np.random.rand(self.n_samples, 2) * 100

    def test_spatial_regression(self):
        """Test spatial regression analysis."""
        from geo_infer_math.core.linalg_tensor import MatrixOperations

        # Create spatial weights matrix
        weights_matrix = MatrixOperations.spatial_weights_matrix(self.coords, k=5)

        result = SpatialLinearAlgebra.solve_spatial_regression(
            self.X, self.y, weights_matrix
        )

        assert 'coefficients' in result
        assert 'standard_errors' in result
        assert 'r_squared' in result
        assert 'residuals' in result

        assert len(result['coefficients']) == self.n_features
        assert 0 <= result['r_squared'] <= 1

    def test_spatial_eigen_analysis(self):
        """Test spatial eigen analysis."""
        from geo_infer_math.core.linalg_tensor import MatrixOperations

        weights_matrix = MatrixOperations.spatial_weights_matrix(self.coords, k=5)

        result = SpatialLinearAlgebra.spatial_eigen_analysis(weights_matrix, n_eigenvectors=5)

        assert 'eigenvalues' in result
        assert 'eigenvectors' in result
        assert len(result['eigenvalues']) == 5
        assert result['eigenvectors'].shape == (self.n_samples, 5)

        # Eigenvalues should be in descending order
        assert np.all(result['eigenvalues'][:-1] >= result['eigenvalues'][1:])

    def test_cholesky_decomposition(self):
        """Test Cholesky decomposition."""
        # Create positive definite matrix
        A = np.array([[4, 2], [2, 3]])
        L = SpatialLinearAlgebra.cholesky_decomposition(A)

        # Check that L is lower triangular
        assert np.allclose(L, np.tril(L))

        # Check that L * L^T = A
        np.testing.assert_array_almost_equal(L @ L.T, A)

    def test_matrix_inverse(self):
        """Test matrix inversion methods."""
        # Test standard inversion
        A = np.array([[1, 2], [3, 4]])
        A_inv = SpatialLinearAlgebra.matrix_inverse(A, method='standard')

        identity = A @ A_inv
        np.testing.assert_array_almost_equal(identity, np.eye(2), decimal=10)

        # Test SVD inversion
        A_inv_svd = SpatialLinearAlgebra.matrix_inverse(A, method='svd')
        identity_svd = A @ A_inv_svd
        np.testing.assert_array_almost_equal(identity_svd, np.eye(2), decimal=5)

    def test_invalid_inverse_method(self):
        """Test handling of invalid inversion method."""
        A = np.eye(2)
        with pytest.raises(ValueError):
            SpatialLinearAlgebra.matrix_inverse(A, method='invalid')
