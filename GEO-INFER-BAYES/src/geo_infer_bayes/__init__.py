"""
GEO-INFER-BAYES: Bayesian inference for geospatial applications
======================================================================

This module provides a comprehensive framework for Bayesian inference
processes within the GEO-INFER ecosystem, implementing probabilistic modeling,
uncertainty quantification, and Bayesian computational methods for geospatial
applications.
"""

__version__ = "0.2.0"
__author__ = "GEO-INFER Team"
__email__ = "geo-infer@activeinference.institute"

import numpy as np
from typing import Any, Optional, Tuple, Type, Union


class SpatialCovariance:
    """Factory for covariance specifications consumed by ``GaussianProcess``."""

    @staticmethod
    def rbf(length_scale: float = 1.0, variance: float = 1.0) -> dict[str, float | str]:
        """Return a squared-exponential covariance specification."""
        return {
            "kernel_type": "rbf",
            "length_scale": length_scale,
            "variance": variance,
        }

    @staticmethod
    def matern_32(
        length_scale: float = 1.0, variance: float = 1.0
    ) -> dict[str, float | str]:
        """Return a Matérn 3/2 covariance specification."""
        return {
            "kernel_type": "matern32",
            "length_scale": length_scale,
            "variance": variance,
        }

    @staticmethod
    def matern_52(
        length_scale: float = 1.0, variance: float = 1.0
    ) -> dict[str, float | str]:
        """Return a Matérn 5/2 covariance specification."""
        return {
            "kernel_type": "matern52",
            "length_scale": length_scale,
            "variance": variance,
        }


# Import main submodules with error handling
try:
    from . import api as _api

    api: Any = _api
except ImportError as e:
    api = None
    import logging

    logging.warning(f"BAYES API module not available: {e}")

try:
    from . import core as _core

    core: Any = _core
except ImportError as e:
    core = None
    import logging

    logging.warning(f"BAYES core module not available: {e}")

try:
    from . import models as _models

    models: Any = _models
except ImportError as e:
    models = None
    import logging

    logging.warning(f"BAYES models module not available: {e}")

try:
    from . import utils as _utils

    utils: Any = _utils
except ImportError as e:
    utils = None
    import logging

    logging.warning(f"BAYES utils module not available: {e}")

# Expose key classes for easy import with error handling
try:
    from .models.spatial_gp import SparseSpatialGP, SpatialGP
except ImportError:
    SpatialGP: Optional[Type[Any]] = None  # type: ignore[no-redef]
    SparseSpatialGP: Optional[Type[Any]] = None  # type: ignore[no-redef]

try:
    from .core.inference import BayesianInference
except ImportError:
    BayesianInference: Optional[Type[Any]] = None  # type: ignore[no-redef]

from .core.variational import VariationalInference  # noqa: E402
from .core.mcmc import MCMC as MCMCSampler  # noqa: E402
from .civic_intel import (  # noqa: E402
    HazardCategoricalPrior,
    build_hazard_categorical_prior,
    build_hazard_prior_table,
    load_crescent_city_intel,
)

try:
    from .core.posterior import PosteriorAnalysis
except ImportError:
    PosteriorAnalysis: Optional[Type[Any]] = None  # type: ignore[no-redef]


class GaussianProcess:
    """
    High-level Gaussian Process interface for geospatial applications.

    Provides a simplified interface for spatial Gaussian process modeling
    with automatic handling of geospatial data structures. Uses an RBF
    (squared exponential) kernel by default, with Cholesky-based exact
    inference for fitting and prediction.

    Parameters
    ----------
    kernel_type : str
        Covariance kernel type: 'rbf', 'matern32', or 'exponential'.
    length_scale : float
        Characteristic length scale of the kernel.
    signal_variance : float
        Signal variance (output scale) of the kernel.
    noise_variance : float
        Observation noise variance.
    jitter : float
        Small diagonal addition for numerical stability.
    """

    def __init__(
        self,
        kernel_type: str = "rbf",
        length_scale: float = 1.0,
        signal_variance: float = 1.0,
        noise_variance: float = 1e-2,
        jitter: float = 1e-6,
        covariance_function: Optional[dict[str, float | str]] = None,
        mean_function: str = "constant",
        **_: object,
    ) -> None:
        if covariance_function is not None:
            kernel_type = str(covariance_function.get("kernel_type", kernel_type))
            length_scale = float(covariance_function.get("length_scale", length_scale))
            signal_variance = float(
                covariance_function.get("variance", signal_variance)
            )
        self.kernel_type = kernel_type
        self.length_scale = length_scale
        self.signal_variance = signal_variance
        self.noise_variance = noise_variance
        self.jitter = jitter
        self.mean_function = mean_function
        self.X_train: Optional[np.ndarray] = None
        self.y_train: Optional[np.ndarray] = None
        self._L: Optional[np.ndarray] = None
        self._alpha: Optional[np.ndarray] = None

    # ------------------------------------------------------------------
    # Kernel functions
    # ------------------------------------------------------------------

    def _compute_kernel(self, X1: np.ndarray, X2: np.ndarray) -> np.ndarray:
        """Compute the kernel (covariance) matrix between two sets of points.

        Parameters
        ----------
        X1 : ndarray of shape (n1, d)
        X2 : ndarray of shape (n2, d)

        Returns
        -------
        K : ndarray of shape (n1, n2)
        """
        sq_dists = self._squared_distances(X1, X2)

        if self.kernel_type == "rbf":
            return np.asarray(
                self.signal_variance * np.exp(-0.5 * sq_dists / (self.length_scale**2))
            )
        elif self.kernel_type == "matern32":
            r = np.sqrt(np.maximum(sq_dists, 0.0)) / self.length_scale
            sqrt3_r = np.sqrt(3.0) * r
            return np.asarray(self.signal_variance * (1.0 + sqrt3_r) * np.exp(-sqrt3_r))
        elif self.kernel_type == "matern52":
            r = np.sqrt(np.maximum(sq_dists, 0.0)) / self.length_scale
            sqrt5_r = np.sqrt(5.0) * r
            return np.asarray(
                self.signal_variance
                * (1.0 + sqrt5_r + (5.0 / 3.0) * r**2)
                * np.exp(-sqrt5_r)
            )
        elif self.kernel_type == "exponential":
            r = np.sqrt(np.maximum(sq_dists, 0.0)) / self.length_scale
            return np.asarray(self.signal_variance * np.exp(-r))
        else:
            raise ValueError(f"Unsupported kernel type: {self.kernel_type}")

    @staticmethod
    def _squared_distances(X1: np.ndarray, X2: np.ndarray) -> np.ndarray:
        """Compute pairwise squared Euclidean distances.

        Parameters
        ----------
        X1 : ndarray of shape (n1, d)
        X2 : ndarray of shape (n2, d)

        Returns
        -------
        D : ndarray of shape (n1, n2)
        """
        X1_sq = np.sum(X1**2, axis=1, keepdims=True)
        X2_sq = np.sum(X2**2, axis=1, keepdims=True)
        return np.asarray(X1_sq + X2_sq.T - 2.0 * X1 @ X2.T)

    # ------------------------------------------------------------------
    # Fit
    # ------------------------------------------------------------------

    def fit(self, X: np.ndarray, y: np.ndarray, **kwargs: Any) -> "GaussianProcess":
        """Fit the Gaussian process model to training data.

        Stores training data, computes the kernel matrix K, and solves
        for alpha = K_inv @ y via Cholesky decomposition for numerical
        stability.

        Parameters
        ----------
        X : ndarray of shape (n_samples, n_features)
            Training input locations.
        y : ndarray of shape (n_samples,)
            Training target values.

        Returns
        -------
        self
        """
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)

        if X.ndim == 1:
            X = X.reshape(-1, 1)

        self.X_train = X
        self.y_train = y

        n = X.shape[0]
        K = self._compute_kernel(X, X)
        K += (self.noise_variance + self.jitter) * np.eye(n)

        # Cholesky decomposition: K = L @ L^T
        self._L = np.linalg.cholesky(K)

        # Solve for alpha: K alpha = y  =>  alpha = K^{-1} y
        # Using forward/back substitution via the Cholesky factor
        z = np.linalg.solve(self._L, y)
        self._alpha = np.linalg.solve(self._L.T, z)

        return self

    # ------------------------------------------------------------------
    # Predict
    # ------------------------------------------------------------------

    def predict(
        self,
        X_new: np.ndarray,
        return_std: bool = True,
    ) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
        """Make predictions with uncertainty quantification.

        Computes the GP predictive mean and (optionally) standard
        deviation at new input locations.

        Parameters
        ----------
        X_new : ndarray of shape (n_new, n_features)
            New input locations.
        return_std : bool
            If True, return both mean and standard deviation.

        Returns
        -------
        mean : ndarray of shape (n_new,)
            Predictive mean.
        std : ndarray of shape (n_new,), optional
            Predictive standard deviation (only when ``return_std=True``).
        """
        if self.X_train is None or self._alpha is None or self._L is None:
            raise RuntimeError(
                "Model has not been fitted. Call fit() before predict()."
            )

        X_new = np.asarray(X_new, dtype=np.float64)
        if X_new.ndim == 1:
            X_new = X_new.reshape(-1, 1)

        # Cross-covariance between training and new points
        K_star = self._compute_kernel(self.X_train, X_new)

        # Predictive mean: mu_* = K_*^T @ alpha
        mean: np.ndarray = np.asarray(K_star.T @ self._alpha)

        if return_std:
            # v = L^{-1} @ K_*
            v = np.linalg.solve(self._L, K_star)

            # Predictive variance: var_* = k(x_*, x_*) - v^T @ v
            K_ss_diag = self.signal_variance * np.ones(X_new.shape[0])
            var = K_ss_diag - np.sum(v**2, axis=0)
            var = np.maximum(var, self.jitter)
            std: np.ndarray = np.asarray(np.sqrt(var))
            return mean, std

        return mean

    def log_marginal_likelihood(self) -> float:
        """Compute the log marginal likelihood of the fitted model.

        Returns
        -------
        lml : float
            Log marginal likelihood: -0.5 * y^T alpha - sum(log(diag(L))) - n/2 * log(2*pi)
        """
        if self.y_train is None or self._alpha is None or self._L is None:
            raise RuntimeError("Model has not been fitted.")

        n = len(self.y_train)
        data_fit = -0.5 * self.y_train @ self._alpha
        complexity = -np.sum(np.log(np.diag(self._L)))
        normalisation = -0.5 * n * np.log(2.0 * np.pi)
        return float(data_fit + complexity + normalisation)


__all__ = [
    "SpatialGP",
    "SparseSpatialGP",
    "BayesianInference",
    "PosteriorAnalysis",
    "GaussianProcess",
    "SpatialCovariance",
    "VariationalInference",
    "MCMCSampler",
    "HazardCategoricalPrior",
    "build_hazard_categorical_prior",
    "build_hazard_prior_table",
    "load_crescent_city_intel",
]
