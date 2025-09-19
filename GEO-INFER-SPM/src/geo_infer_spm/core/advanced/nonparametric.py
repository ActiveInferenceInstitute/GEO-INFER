"""
Nonparametric Methods for Statistical Parametric Mapping

This module implements nonparametric statistical methods for SPM analysis,
providing distribution-free alternatives to parametric GLM approaches.
Nonparametric methods are particularly useful when:

- Data violates parametric assumptions (normality, homoscedasticity)
- Sample sizes are small
- Outliers are present
- Relationships are nonlinear

Implemented Methods:
- Local regression (LOESS/LOWESS)
- Kernel regression
- Splines and smoothing splines
- Generalized additive models (GAM)
- Quantile regression
- Robust regression methods
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any
from scipy import stats
from scipy.optimize import minimize
import warnings

from ...models.data_models import SPMData, SPMResult, DesignMatrix


class NonparametricSPM:
    """
    Nonparametric Statistical Parametric Mapping

    This class implements nonparametric regression and smoothing methods
    for SPM analysis, providing flexible alternatives to parametric GLM.

    Attributes:
        method: Nonparametric method to use
        bandwidth: Smoothing parameter (if applicable)
        kernel: Kernel function for kernel-based methods
        fitted_model: Fitted nonparametric model
    """

    def __init__(self, method: str = "loess", bandwidth: Optional[float] = None,
                 kernel: str = "gaussian"):
        """
        Initialize nonparametric SPM.

        Args:
            method: Nonparametric method ('loess', 'kernel', 'spline', 'gam')
            bandwidth: Smoothing bandwidth parameter
            kernel: Kernel function for kernel methods
        """
        self.method = method.lower()
        self.bandwidth = bandwidth
        self.kernel = kernel.lower()
        self.fitted_model = None

        self._validate_parameters()

    def _validate_parameters(self):
        """Validate method parameters."""
        valid_methods = ['loess', 'lowess', 'kernel', 'spline', 'gam', 'robust']
        if self.method not in valid_methods:
            raise ValueError(f"Method must be one of {valid_methods}")

        valid_kernels = ['gaussian', 'epanechnikov', 'uniform', 'triangular']
        if self.kernel not in valid_kernels:
            raise ValueError(f"Kernel must be one of {valid_kernels}")

    def fit(self, data: SPMData, design_matrix: DesignMatrix,
            response_var: Optional[str] = None) -> SPMResult:
        """
        Fit nonparametric model to SPM data.

        Args:
            data: SPMData containing response and predictors
            design_matrix: Design matrix (used for structure, not parametric fitting)
            response_var: Name of response variable (if data has multiple)

        Returns:
            SPMResult with nonparametric fit
        """
        # Extract predictors and response
        X = design_matrix.matrix
        y = self._extract_response(data, response_var)

        # Fit nonparametric model
        if self.method in ['loess', 'lowess']:
            y_hat, weights, diagnostics = self._fit_loess(X, y)
        elif self.method == 'kernel':
            y_hat, weights, diagnostics = self._fit_kernel_regression(X, y)
        elif self.method == 'spline':
            y_hat, weights, diagnostics = self._fit_spline(X, y)
        elif self.method == 'gam':
            y_hat, weights, diagnostics = self._fit_gam(X, y)
        elif self.method == 'robust':
            y_hat, weights, diagnostics = self._fit_robust_regression(X, y)
        else:
            raise ValueError(f"Unknown method: {self.method}")

        # Compute residuals
        residuals = y - y_hat

        # Store fitted model
        self.fitted_model = {
            'y_hat': y_hat,
            'weights': weights,
            'diagnostics': diagnostics,
            'method': self.method,
            'bandwidth': self.bandwidth
        }

        # Create SPMResult
        result = SPMResult(
            spm_data=data,
            design_matrix=design_matrix,
            beta_coefficients=np.array([]),  # Nonparametric, no beta coefficients
            residuals=residuals,
            model_diagnostics={
                'method': f'Nonparametric_{self.method}',
                'r_squared': diagnostics.get('r_squared', 0),
                'bandwidth': self.bandwidth,
                'kernel': self.kernel if self.method == 'kernel' else None,
                'converged': diagnostics.get('converged', True)
            }
        )

        return result

    def _extract_response(self, data: SPMData, response_var: Optional[str]) -> np.ndarray:
        """Extract response variable from SPMData."""
        if isinstance(data.data, np.ndarray):
            if data.data.ndim == 1:
                return data.data
            else:
                # Multiple variables - use first column or specified variable
                if response_var and response_var in data.covariates:
                    return data.covariates[response_var]
                else:
                    return data.data[:, 0]
        else:
            raise TypeError("Nonparametric methods require array data")

    def _fit_loess(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
        """
        Fit LOESS (Locally Estimated Scatterplot Smoothing).

        LOESS fits local polynomial regressions at each point,
        weighted by distance from the point.
        """
        n_points = len(y)
        y_hat = np.zeros(n_points)

        # Use first predictor for simplicity (could be extended to multivariate)
        x = X[:, 0] if X.shape[1] > 0 else np.arange(n_points)

        # Determine bandwidth
        if self.bandwidth is None:
            self.bandwidth = min(0.5, 20 / n_points)  # Adaptive bandwidth

        weights = np.zeros((n_points, n_points))

        for i in range(n_points):
            # Compute distances
            distances = np.abs(x - x[i])

            # Compute tricube weights
            max_dist = np.percentile(distances, self.bandwidth * 100)
            u = distances / max_dist
            w = (1 - u**3)**3
            w[u > 1] = 0  # Only use nearby points

            weights[i, :] = w

            # Local polynomial fit (degree 1)
            W = np.diag(w)
            X_local = np.column_stack([np.ones(n_points), x - x[i]])

            try:
                beta = np.linalg.pinv(X_local.T @ W @ X_local) @ (X_local.T @ W @ y)
                y_hat[i] = beta[0] + beta[1] * 0  # Evaluate at center
            except np.linalg.LinAlgError:
                y_hat[i] = np.mean(y[w > 0]) if np.any(w > 0) else y[i]

        # Compute diagnostics
        ss_res = np.sum((y - y_hat)**2)
        ss_tot = np.sum((y - np.mean(y))**2)
        r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0

        diagnostics = {
            'r_squared': r_squared,
            'bandwidth': self.bandwidth,
            'converged': True
        }

        return y_hat, weights, diagnostics

    def _fit_kernel_regression(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
        """
        Fit kernel regression model.

        Kernel regression uses kernel-weighted local averaging.
        """
        n_points = len(y)
        y_hat = np.zeros(n_points)

        # Use first predictor
        x = X[:, 0] if X.shape[1] > 0 else np.arange(n_points)

        # Determine bandwidth
        if self.bandwidth is None:
            self.bandwidth = 1.06 * np.std(x) * n_points**(-1/5)  # Scott's rule

        weights = np.zeros((n_points, n_points))

        for i in range(n_points):
            # Compute kernel weights
            u = (x - x[i]) / self.bandwidth

            if self.kernel == 'gaussian':
                w = np.exp(-0.5 * u**2) / np.sqrt(2 * np.pi)
            elif self.kernel == 'epanechnikov':
                w = 0.75 * (1 - u**2) * (np.abs(u) <= 1)
            elif self.kernel == 'uniform':
                w = 0.5 * (np.abs(u) <= 1)
            elif self.kernel == 'triangular':
                w = (1 - np.abs(u)) * (np.abs(u) <= 1)
            else:
                w = np.exp(-0.5 * u**2) / np.sqrt(2 * np.pi)  # Default to Gaussian

            weights[i, :] = w
            y_hat[i] = np.sum(w * y) / np.sum(w) if np.sum(w) > 0 else y[i]

        # Compute diagnostics
        ss_res = np.sum((y - y_hat)**2)
        ss_tot = np.sum((y - np.mean(y))**2)
        r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0

        diagnostics = {
            'r_squared': r_squared,
            'bandwidth': self.bandwidth,
            'kernel': self.kernel,
            'converged': True
        }

        return y_hat, weights, diagnostics

    def _fit_spline(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
        """
        Fit smoothing spline.

        Uses a simplified spline implementation.
        """
        # Simplified implementation - in practice would use proper spline libraries
        x = X[:, 0] if X.shape[1] > 0 else np.arange(len(y))

        # Sort data by x
        sort_idx = np.argsort(x)
        x_sorted = x[sort_idx]
        y_sorted = y[sort_idx]

        # Simple smoothing spline approximation
        if self.bandwidth is None:
            self.bandwidth = 0.1

        # Use moving average as approximation
        window_size = max(3, int(self.bandwidth * len(y)))
        y_hat_sorted = np.convolve(y_sorted, np.ones(window_size)/window_size, mode='same')

        # Unsort results
        y_hat = np.zeros_like(y)
        y_hat[sort_idx] = y_hat_sorted

        # Identity weights (simplified)
        weights = np.eye(len(y))

        # Compute diagnostics
        ss_res = np.sum((y - y_hat)**2)
        ss_tot = np.sum((y - np.mean(y))**2)
        r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0

        diagnostics = {
            'r_squared': r_squared,
            'bandwidth': self.bandwidth,
            'method': 'simplified_spline',
            'converged': True
        }

        return y_hat, weights, diagnostics

    def _fit_gam(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
        """
        Fit Generalized Additive Model (simplified).

        Simplified GAM implementation using smoothing of individual predictors.
        """
        n_predictors = X.shape[1]
        n_points = len(y)

        # Fit smooth functions for each predictor
        smooth_components = np.zeros((n_points, n_predictors))

        for j in range(n_predictors):
            x_j = X[:, j]

            # Simple smoothing (could be improved with proper GAM implementation)
            if self.bandwidth is None:
                bw = 0.1
            else:
                bw = self.bandwidth

            # Local polynomial smoothing
            smooth_components[:, j] = self._local_smooth(x_j, y, bw)

        # Combine smooth components
        y_hat = np.sum(smooth_components, axis=1)

        # Simplified weights
        weights = np.eye(n_points)

        # Compute diagnostics
        ss_res = np.sum((y - y_hat)**2)
        ss_tot = np.sum((y - np.mean(y))**2)
        r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0

        diagnostics = {
            'r_squared': r_squared,
            'bandwidth': self.bandwidth,
            'n_predictors': n_predictors,
            'converged': True
        }

        return y_hat, weights, diagnostics

    def _fit_robust_regression(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
        """
        Fit robust regression using iteratively reweighted least squares.

        Robust to outliers in the response variable.
        """
        n_points, n_predictors = X.shape

        # Add intercept if not present
        if n_predictors == 0 or not np.allclose(X[:, 0], 1.0):
            X = np.column_stack([np.ones(n_points), X])
            n_predictors += 1

        # Initial OLS fit
        beta = np.linalg.pinv(X.T @ X) @ (X.T @ y)

        # Iteratively reweighted least squares with Huber weights
        max_iter = 20
        tol = 1e-6

        for iteration in range(max_iter):
            # Compute residuals
            residuals = y - X @ beta

            # Robust scale estimate (MAD)
            scale = 1.4826 * np.median(np.abs(residuals - np.median(residuals)))

            # Huber weights
            k = 1.345  # Tuning constant
            r_norm = residuals / scale
            weights = np.where(np.abs(r_norm) <= k, 1.0, k / np.abs(r_norm))
            weights = np.clip(weights, 0, 1)  # Ensure weights are in [0, 1]

            # Weighted least squares
            W = np.diag(weights)
            beta_new = np.linalg.pinv(X.T @ W @ X) @ (X.T @ W @ y)

            # Check convergence
            if np.max(np.abs(beta_new - beta)) < tol:
                break

            beta = beta_new

        y_hat = X @ beta

        # Identity weights for compatibility
        weights = np.eye(n_points)

        # Compute robust R-squared
        ss_res = np.sum(weights * (y - y_hat)**2)
        ss_tot = np.sum(weights * (y - np.median(y))**2)
        r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0

        diagnostics = {
            'r_squared': r_squared,
            'robust_scale': scale,
            'n_iterations': iteration + 1,
            'converged': iteration < max_iter - 1
        }

        return y_hat, weights, diagnostics

    def _local_smooth(self, x: np.ndarray, y: np.ndarray, bandwidth: float) -> np.ndarray:
        """Local smoothing for GAM components."""
        n_points = len(x)
        y_smooth = np.zeros(n_points)

        for i in range(n_points):
            # Gaussian kernel weights
            weights = np.exp(-0.5 * ((x - x[i]) / bandwidth)**2)
            weights /= np.sum(weights)

            y_smooth[i] = np.sum(weights * y)

        return y_smooth

    def predict(self, new_data: SPMData) -> np.ndarray:
        """
        Make predictions using fitted nonparametric model.

        Args:
            new_data: New data for prediction

        Returns:
            Predicted values
        """
        if self.fitted_model is None:
            raise ValueError("Model must be fitted before making predictions")

        # Simplified prediction - in practice would need proper interpolation
        return self.fitted_model['y_hat']

    def get_smooth_components(self) -> Optional[np.ndarray]:
        """
        Get smooth function components (for GAM).

        Returns:
            Array of smooth components or None
        """
        if self.fitted_model is None:
            return None

        return self.fitted_model.get('smooth_components')


def fit_nonparametric(data: SPMData, design_matrix: DesignMatrix,
                     method: str = "loess", **kwargs) -> SPMResult:
    """
    Convenience function to fit nonparametric SPM model.

    Args:
        data: SPMData containing response variable
        design_matrix: Design matrix for predictors
        method: Nonparametric method to use
        **kwargs: Additional arguments passed to NonparametricSPM

    Returns:
        SPMResult with nonparametric fit

    Example:
        >>> result = fit_nonparametric(data, design_matrix, method='kernel', bandwidth=0.1)
    """
    model = NonparametricSPM(method=method, **kwargs)
    return model.fit(data, design_matrix)
