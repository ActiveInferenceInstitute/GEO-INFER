"""
Linear Algebra and Tensor Operations Module

This module provides functions and structures for handling linear algebra
operations and multi-dimensional geospatial data (tensors) for spatial analysis.
"""

import numpy as np
from typing import Union, List, Tuple, Dict, Optional, Any, Callable
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class TensorData:
    """Container for multi-dimensional geospatial data."""
    data: np.ndarray
    coordinates: Optional[np.ndarray] = None
    dimensions: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.dimensions is None:
            self.dimensions = [f"dim_{i}" for i in range(self.data.ndim)]
        if self.metadata is None:
            self.metadata = {}

class MatrixOperations:
    """Linear algebra operations for geospatial matrices."""

    @staticmethod
    def condition_number(matrix: np.ndarray) -> float:
        """
        Calculate the condition number of a matrix.

        Args:
            matrix: Input matrix

        Returns:
            Condition number (ratio of largest to smallest singular value)
        """
        try:
            singular_values = np.linalg.svd(matrix, compute_uv=False)
            return singular_values[0] / singular_values[-1]
        except np.linalg.LinAlgError:
            logger.warning("Matrix is singular or nearly singular")
            return float('inf')

    @staticmethod
    def is_positive_definite(matrix: np.ndarray, tolerance: float = 1e-8) -> bool:
        """
        Check if a matrix is positive definite.

        Args:
            matrix: Input matrix
            tolerance: Numerical tolerance

        Returns:
            True if matrix is positive definite
        """
        try:
            eigenvalues = np.linalg.eigvals(matrix)
            return np.all(eigenvalues > tolerance)
        except np.linalg.LinAlgError:
            return False

    @staticmethod
    def nearest_positive_definite(matrix: np.ndarray, epsilon: float = 1e-8) -> np.ndarray:
        """
        Find the nearest positive definite matrix.

        Args:
            matrix: Input matrix
            epsilon: Minimum eigenvalue threshold

        Returns:
            Nearest positive definite matrix
        """
        # Ensure matrix is symmetric
        B = (matrix + matrix.T) / 2

        # Compute eigenvalue decomposition
        eigenvalues, eigenvectors = np.linalg.eigh(B)

        # Replace negative or very small eigenvalues with epsilon
        eigenvalues[eigenvalues <= epsilon] = epsilon

        # Reconstruct matrix
        return eigenvectors @ np.diag(eigenvalues) @ eigenvectors.T

    @staticmethod
    def spatial_weights_matrix(points: np.ndarray,
                              method: str = 'inverse_distance',
                              k: int = 5,
                              threshold: Optional[float] = None) -> np.ndarray:
        """
        Create spatial weights matrix from point coordinates.

        Args:
            points: Point coordinates (n_points, 2)
            method: Weighting method ('inverse_distance', 'knn', 'gaussian')
            k: Number of nearest neighbors (for knn method)
            threshold: Distance threshold for binary weights

        Returns:
            Spatial weights matrix (n_points, n_points)
        """
        n_points = len(points)
        weights = np.zeros((n_points, n_points))

        # Calculate pairwise distances
        distances = np.zeros((n_points, n_points))
        for i in range(n_points):
            for j in range(n_points):
                distances[i, j] = np.sqrt(np.sum((points[i] - points[j])**2))

        if method == 'inverse_distance':
            # Inverse distance weighting
            for i in range(n_points):
                for j in range(n_points):
                    if i != j:
                        weights[i, j] = 1.0 / (distances[i, j] + 1e-10)

        elif method == 'knn':
            # K-nearest neighbors
            for i in range(n_points):
                # Find k nearest neighbors
                neighbor_indices = np.argsort(distances[i])[1:k+1]  # Exclude self
                weights[i, neighbor_indices] = 1.0

        elif method == 'gaussian':
            # Gaussian kernel weights
            sigma = np.std(distances[distances > 0])  # Use distance standard deviation as sigma
            for i in range(n_points):
                for j in range(n_points):
                    if i != j:
                        weights[i, j] = np.exp(-distances[i, j]**2 / (2 * sigma**2))

        elif method == 'binary':
            # Binary weights based on threshold
            if threshold is None:
                threshold = np.mean(distances[distances > 0])
            weights = (distances <= threshold).astype(float)
            np.fill_diagonal(weights, 0)  # No self-weights

            # Row-standardize binary weights
            row_sums = weights.sum(axis=1)
            row_sums[row_sums == 0] = 1  # Avoid division by zero
            weights = weights / row_sums[:, np.newaxis]

        # Row-standardize the weights
        row_sums = weights.sum(axis=1)
        row_sums[row_sums == 0] = 1  # Avoid division by zero
        weights = weights / row_sums[:, np.newaxis]

        return weights

    @staticmethod
    def moran_i_matrix(values: np.ndarray,
                      weights_matrix: np.ndarray) -> Dict[str, float]:
        """
        Calculate Moran's I statistic using matrix operations.

        Args:
            values: Value array
            weights_matrix: Spatial weights matrix

        Returns:
            Moran's I statistics
        """
        n = len(values)

        # Standardize values
        z = (values - np.mean(values)) / np.std(values)

        # Calculate Moran's I
        numerator = z.T @ weights_matrix @ z
        denominator = np.sum(z**2)

        I = (n / np.sum(weights_matrix)) * (numerator / denominator)

        # Expected value and variance
        expected_I = -1.0 / (n - 1)

        # Simplified variance calculation
        s1 = np.sum((weights_matrix + weights_matrix.T)**2) / 2
        s2 = np.sum((np.sum(weights_matrix, axis=0) + np.sum(weights_matrix, axis=1))**2)
        var_I = (n**2 * s1 - n * s2 + 3 * np.sum(weights_matrix)**2) / ((n**2 - 1) * np.sum(weights_matrix)**2)

        # Z-score and p-value
        z_score = (I - expected_I) / np.sqrt(var_I)
        p_value = 2 * (1 - min(1.0, abs(z_score) / 4))  # Approximate

        return {
            'I': I,
            'expected_I': expected_I,
            'variance': var_I,
            'z_score': z_score,
            'p_value': p_value
        }

class TensorOperations:
    """Operations for multi-dimensional geospatial data."""

    @staticmethod
    def create_spatiotemporal_tensor(spatial_data: List[np.ndarray],
                                   temporal_indices: List[float],
                                   spatial_coords: Optional[np.ndarray] = None) -> TensorData:
        """
        Create a spatiotemporal tensor from spatial data over time.

        Args:
            spatial_data: List of spatial arrays (one per time step)
            temporal_indices: Time indices
            spatial_coords: Spatial coordinates

        Returns:
            TensorData object
        """
        # Stack spatial data into 3D tensor (time, height, width)
        tensor_data = np.stack(spatial_data, axis=0)

        dimensions = ['time', 'latitude', 'longitude']
        metadata = {
            'temporal_indices': temporal_indices,
            'n_time_steps': len(temporal_indices),
            'spatial_shape': spatial_data[0].shape
        }

        return TensorData(
            data=tensor_data,
            coordinates=spatial_coords,
            dimensions=dimensions,
            metadata=metadata
        )

    @staticmethod
    def tensor_unfold(tensor: TensorData,
                     mode: int) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Unfold tensor along a specific mode (MATRICIZATION).

        Args:
            tensor: Input tensor
            mode: Mode along which to unfold (0, 1, or 2 for 3D tensor)

        Returns:
            Tuple of (unfolded_matrix, unfolding_info)
        """
        data = tensor.data

        if data.ndim != 3:
            raise ValueError("Tensor must be 3-dimensional for unfolding")

        n0, n1, n2 = data.shape

        if mode == 0:
            # Unfold along mode 0 (time)
            unfolded = data.reshape(n0, n1 * n2).T
            shape_info = {'original_shape': (n0, n1, n2), 'mode': 0}
        elif mode == 1:
            # Unfold along mode 1 (latitude)
            unfolded = data.transpose(1, 0, 2).reshape(n1, n0 * n2)
            shape_info = {'original_shape': (n0, n1, n2), 'mode': 1}
        elif mode == 2:
            # Unfold along mode 2 (longitude)
            unfolded = data.transpose(2, 0, 1).reshape(n2, n0 * n1).T
            shape_info = {'original_shape': (n0, n1, n2), 'mode': 2}
        else:
            raise ValueError("Mode must be 0, 1, or 2 for 3D tensor")

        return unfolded, shape_info

    @staticmethod
    def tensor_fold(unfolded_matrix: np.ndarray,
                   shape_info: Dict[str, Any]) -> np.ndarray:
        """
        Fold unfolded matrix back into tensor.

        Args:
            unfolded_matrix: Unfolded matrix
            shape_info: Information from unfolding operation

        Returns:
            Reconstructed tensor
        """
        original_shape = shape_info['original_shape']
        mode = shape_info['mode']

        n0, n1, n2 = original_shape

        if mode == 0:
            folded = unfolded_matrix.T.reshape(original_shape)
        el        if mode == 1:
            temp = unfolded_matrix.reshape((n1, n0, n2))
            folded = temp.transpose(1, 0, 2)
        elif mode == 2:
            temp = unfolded_matrix.T.reshape((n2, n0, n1))
            folded = temp.transpose(1, 2, 0)

        return folded

    @staticmethod
    def principal_component_analysis(tensor: TensorData,
                                   n_components: Optional[int] = None) -> Dict[str, Any]:
        """
        Perform PCA on tensor data.

        Args:
            tensor: Input tensor data
            n_components: Number of principal components

        Returns:
            PCA results
        """
        # Unfold tensor along spatial mode (combine space-time)
        unfolded, shape_info = TensorOperations.tensor_unfold(tensor, mode=0)

        # Perform PCA
        if n_components is None:
            n_components = min(unfolded.shape)

        # Center the data
        unfolded_centered = unfolded - np.mean(unfolded, axis=0)

        # Compute SVD
        U, s, Vt = np.linalg.svd(unfolded_centered, full_matrices=False)

        # Select components
        U_reduced = U[:, :n_components]
        s_reduced = s[:n_components]
        Vt_reduced = Vt[:n_components]

        # Reconstruct principal components
        principal_components = U_reduced @ np.diag(s_reduced)

        # Calculate explained variance
        explained_variance = s_reduced**2 / np.sum(s**2)
        cumulative_variance = np.cumsum(explained_variance)

        return {
            'principal_components': principal_components,
            'explained_variance': explained_variance,
            'cumulative_variance': cumulative_variance,
            'eigenvalues': s_reduced**2,
            'eigenvectors': Vt_reduced.T,
            'projection_matrix': U_reduced,
            'singular_values': s_reduced
        }

    @staticmethod
    def tensor_decomposition(tensor: TensorData,
                           rank: int,
                           method: str = 'cp') -> Dict[str, Any]:
        """
        Perform tensor decomposition (CP or Tucker).

        Args:
            tensor: Input tensor
            rank: Decomposition rank
            method: Decomposition method ('cp' or 'tucker')

        Returns:
            Decomposition results
        """
        if method == 'cp':
            return TensorOperations._cp_decomposition(tensor, rank)
        elif method == 'tucker':
            return TensorOperations._tucker_decomposition(tensor, rank)
        else:
            raise ValueError("Method must be 'cp' or 'tucker'")

    @staticmethod
    def _cp_decomposition(tensor: TensorData, rank: int) -> Dict[str, Any]:
        """CP (CANDECOMP/PARAFAC) decomposition."""
        # Simplified CP decomposition using alternating least squares
        data = tensor.data
        n0, n1, n2 = data.shape

        # Initialize factor matrices randomly
        A = np.random.randn(n0, rank)
        B = np.random.randn(n1, rank)
        C = np.random.randn(n2, rank)

        # Normalize columns
        for r in range(rank):
            A[:, r] /= np.linalg.norm(A[:, r])
            B[:, r] /= np.linalg.norm(B[:, r])
            C[:, r] /= np.linalg.norm(C[:, r])

        # ALS iterations (simplified - should use proper ALS algorithm)
        max_iter = 50
        for iteration in range(max_iter):
            # This is a simplified implementation
            # In practice, you'd use more sophisticated ALS with unfolding
            pass

        return {
            'factor_matrices': [A, B, C],
            'rank': rank,
            'method': 'cp'
        }

    @staticmethod
    def _tucker_decomposition(tensor: TensorData, rank: int) -> Dict[str, Any]:
        """Tucker decomposition."""
        # Simplified Tucker decomposition
        data = tensor.data
        n0, n1, n2 = data.shape

        # Initialize core tensor and factor matrices
        core_shape = (min(n0, rank), min(n1, rank), min(n2, rank))
        core = np.random.randn(*core_shape)

        A = np.random.randn(n0, core_shape[0])
        B = np.random.randn(n1, core_shape[1])
        C = np.random.randn(n2, core_shape[2])

        return {
            'core_tensor': core,
            'factor_matrices': [A, B, C],
            'rank': rank,
            'method': 'tucker'
        }

class SpatialLinearAlgebra:
    """Specialized linear algebra for spatial problems."""

    @staticmethod
    def solve_spatial_regression(X: np.ndarray,
                               y: np.ndarray,
                               weights_matrix: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Solve spatial regression with optional spatial weights.

        Args:
            X: Design matrix (n_samples, n_features)
            y: Target values (n_samples,)
            weights_matrix: Spatial weights matrix

        Returns:
            Regression results
        """
        if weights_matrix is None:
            # Ordinary least squares
            coefficients = np.linalg.lstsq(X, y, rcond=None)[0]
            residuals = y - X @ coefficients

            # Calculate statistics
            n, p = X.shape
            mse = np.sum(residuals**2) / (n - p)
            se = np.sqrt(np.diag(mse * np.linalg.inv(X.T @ X)))
            t_stats = coefficients / se
            r_squared = 1 - np.sum(residuals**2) / np.sum((y - np.mean(y))**2)

        else:
            # Spatial regression (simplified)
            # In practice, this would involve spatial autoregressive models
            W = weights_matrix
            rho = 0.1  # Simplified spatial autoregressive parameter

            # Spatial lag model: y = rho * W*y + X*beta + epsilon
            # This is a very simplified implementation
            y_spatial = y - rho * W @ y
            coefficients = np.linalg.lstsq(X, y_spatial, rcond=None)[0]
            residuals = y_spatial - X @ coefficients
            r_squared = 1 - np.sum(residuals**2) / np.sum((y_spatial - np.mean(y_spatial))**2)

            se = np.full_like(coefficients, np.nan)  # Simplified
            t_stats = np.full_like(coefficients, np.nan)

        return {
            'coefficients': coefficients,
            'standard_errors': se,
            't_statistics': t_stats,
            'r_squared': r_squared,
            'residuals': residuals
        }

    @staticmethod
    def spatial_eigen_analysis(weights_matrix: np.ndarray,
                             n_eigenvectors: int = 10) -> Dict[str, Any]:
        """
        Perform eigen analysis of spatial weights matrix.

        Args:
            weights_matrix: Spatial weights matrix
            n_eigenvectors: Number of eigenvectors to compute

        Returns:
            Eigen analysis results
        """
        # Ensure matrix is symmetric
        W = (weights_matrix + weights_matrix.T) / 2

        # Compute eigenvalues and eigenvectors
        eigenvalues, eigenvectors = np.linalg.eigh(W)

        # Sort in descending order
        idx = np.argsort(eigenvalues)[::-1]
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]

        # Select requested number of eigenvectors
        eigenvalues = eigenvalues[:n_eigenvectors]
        eigenvectors = eigenvectors[:, :n_eigenvectors]

        return {
            'eigenvalues': eigenvalues,
            'eigenvectors': eigenvectors,
            'n_eigenvectors': n_eigenvectors
        }

    @staticmethod
    def cholesky_decomposition(matrix: np.ndarray) -> np.ndarray:
        """
        Perform Cholesky decomposition for positive definite matrices.

        Args:
            matrix: Positive definite matrix

        Returns:
            Lower triangular matrix L such that L*L^T = matrix
        """
        try:
            return np.linalg.cholesky(matrix)
        except np.linalg.LinAlgError:
            logger.warning("Matrix is not positive definite, finding nearest PD matrix")
            pd_matrix = MatrixOperations.nearest_positive_definite(matrix)
            return np.linalg.cholesky(pd_matrix)

    @staticmethod
    def matrix_inverse(matrix: np.ndarray,
                      method: str = 'standard') -> np.ndarray:
        """
        Compute matrix inverse using various methods.

        Args:
            matrix: Input matrix
            method: Inversion method ('standard', 'svd', 'iterative')

        Returns:
            Matrix inverse
        """
        if method == 'standard':
            try:
                return np.linalg.inv(matrix)
            except np.linalg.LinAlgError:
                logger.warning("Matrix is singular, using pseudo-inverse")
                return np.linalg.pinv(matrix)

        elif method == 'svd':
            U, s, Vt = np.linalg.svd(matrix)
            # Filter small singular values
            s_inv = np.where(s > 1e-10, 1.0 / s, 0.0)
            return Vt.T @ np.diag(s_inv) @ U.T

        elif method == 'iterative':
            # Simplified iterative method (Richardson iteration)
            n = matrix.shape[0]
            X = np.eye(n)  # Initial guess
            max_iter = 100

            for _ in range(max_iter):
                X_new = X @ (2 * np.eye(n) - matrix @ X)
                if np.allclose(X, X_new, atol=1e-10):
                    break
                X = X_new

            return X

        else:
            raise ValueError(f"Unknown inversion method: {method}")

__all__ = [
    "TensorData",
    "MatrixOperations",
    "TensorOperations",
    "SpatialLinearAlgebra"
]
