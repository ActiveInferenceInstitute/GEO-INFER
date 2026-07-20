"""
Prior distributions for Bayesian geospatial models.

This module provides prior distribution classes for Bayesian
inference in geospatial applications.
"""

import numpy as np


class SpatialPrior:
    """
    Spatial prior distributions for Bayesian models.

    This class provides methods for defining spatial priors
    that account for spatial structure in the data.
    """

    def __init__(self, prior_type: str = 'icar', **kwargs):
        """
        Initialize the spatial prior.

        Args:
            prior_type: Type of spatial prior ('icar', 'bym', 'leroux')
            **kwargs: Additional parameters for the prior
        """
        self.prior_type = prior_type.lower()
        self.parameters = kwargs

    def log_prior(self, spatial_field: np.ndarray, adjacency_matrix: np.ndarray) -> float:
        """
        Compute the log prior for a spatial field.

        Args:
            spatial_field: Spatial field values
            adjacency_matrix: Adjacency matrix defining spatial relationships

        Returns:
            Log prior value
        """
        if self.prior_type == 'icar':
            return self._icar_prior(spatial_field, adjacency_matrix)
        elif self.prior_type == 'bym':
            return self._bym_prior(spatial_field, adjacency_matrix)
        elif self.prior_type == 'leroux':
            return self._leroux_prior(spatial_field, adjacency_matrix)
        else:
            raise ValueError(f"Unknown spatial prior type: {self.prior_type}")

    def _icar_prior(self, phi: np.ndarray, W: np.ndarray) -> float:
        """Intrinsic Conditional Autoregressive (ICAR) prior.

        Implements the pairwise difference ICAR prior:
            phi ~ ICAR(tau)  =>  log p(phi) ∝ (n/2)ln(tau) - (tau/2) phi^T Q phi
        where Q = tau * (D - W) is the graph Laplacian precision matrix,
        D = diag(W 1) is the degree matrix.

        Reference: Besag (1974), Rue & Held (2005) Gaussian Markov Random Fields.
        """
        n = len(phi)
        tau = self.parameters.get('tau', 1.0)

        # Compute the precision matrix
        Q = tau * (np.diag(W @ np.ones(n)) - W)

        # Log prior (up to constant)
        log_prior = 0.5 * n * np.log(tau) - 0.5 * tau * phi.T @ Q @ phi

        return log_prior

    def _bym_prior(self, phi: np.ndarray, W: np.ndarray) -> float:
        """Besag-York-Mollié (BYM) prior.

        Combines spatially-structured ICAR component with an unstructured
        IID noise component via mixing weight alpha in [0, 1]:
            Q = (1 - alpha) * tau * I  +  alpha * tau * (D - W)

        Reference: Besag, York & Mollié (1991).
        """
        alpha = self.parameters.get('alpha', 0.5)
        tau = self.parameters.get('tau', 1.0)

        n = len(phi)
        Q_icar = tau * (np.diag(W @ np.ones(n)) - W)
        Q_iid = tau * np.eye(n)

        # Combined precision matrix
        Q = (1 - alpha) * Q_iid + alpha * Q_icar

        log_prior = 0.5 * n * np.log(tau) - 0.5 * tau * phi.T @ Q @ phi

        return log_prior

    def _leroux_prior(self, phi: np.ndarray, W: np.ndarray) -> float:
        """Leroux prior with tunable spatial autocorrelation.

        Interpolates between IID (rho=0) and ICAR (rho=1) via:
            Q = tau * (D - rho * W)  where rho in [0, 1)

        Reference: Leroux, Lei & Breslow (1999).
        """
        rho = self.parameters.get('rho', 0.5)
        tau = self.parameters.get('tau', 1.0)

        n = len(phi)
        D = np.diag(W @ np.ones(n))
        Q = tau * (D - rho * W)

        log_prior = 0.5 * n * np.log(tau) - 0.5 * tau * phi.T @ Q @ phi

        return log_prior


class TemporalPrior:
    """
    Temporal prior distributions for Bayesian models.

    This class provides methods for defining temporal priors
    for time series and spatio-temporal models.
    """

    def __init__(self, prior_type: str = 'ar1', **kwargs):
        """
        Initialize the temporal prior.

        Args:
            prior_type: Type of temporal prior ('ar1', 'rw1', 'rw2')
            **kwargs: Additional parameters for the prior
        """
        self.prior_type = prior_type.lower()
        self.parameters = kwargs

    def log_prior(self, temporal_field: np.ndarray) -> float:
        """
        Compute the log prior for a temporal field.

        Args:
            temporal_field: Temporal field values

        Returns:
            Log prior value
        """
        if self.prior_type == 'ar1':
            return self._ar1_prior(temporal_field)
        elif self.prior_type == 'rw1':
            return self._rw1_prior(temporal_field)
        elif self.prior_type == 'rw2':
            return self._rw2_prior(temporal_field)
        else:
            raise ValueError(f"Unknown temporal prior type: {self.prior_type}")

    def _ar1_prior(self, x: np.ndarray) -> float:
        """First-order autoregressive (AR(1)) prior."""
        phi = self.parameters.get('phi', 0.5)
        tau = self.parameters.get('tau', 1.0)

        # Compute differences
        diffs = x[1:] - phi * x[:-1]

        # Log prior
        log_prior = 0.5 * (len(x) - 1) * np.log(tau) - 0.5 * tau * np.sum(diffs**2)

        return log_prior

    def _rw1_prior(self, x: np.ndarray) -> float:
        """Random walk of order 1 (RW1) prior."""
        tau = self.parameters.get('tau', 1.0)

        # Compute first differences
        diffs = x[1:] - x[:-1]

        # Log prior
        log_prior = 0.5 * (len(x) - 1) * np.log(tau) - 0.5 * tau * np.sum(diffs**2)

        return log_prior

    def _rw2_prior(self, x: np.ndarray) -> float:
        """Random walk of order 2 (RW2) prior."""
        tau = self.parameters.get('tau', 1.0)

        # Compute second differences
        diffs = x[2:] - 2 * x[1:-1] + x[:-2]

        # Log prior
        log_prior = 0.5 * (len(x) - 2) * np.log(tau) - 0.5 * tau * np.sum(diffs**2)

        return log_prior


class GaussianProcessPrior:
    """
    Gaussian Process prior distributions for Bayesian models.

    This class provides GP priors for spatial and spatio-temporal models.
    """

    def __init__(self, kernel: str = 'matern', **kwargs):
        """
        Initialize the Gaussian Process prior.

        Args:
            kernel: Type of covariance kernel ('matern', 'rbf', 'exponential')
            **kwargs: Additional parameters for the kernel
        """
        self.kernel = kernel.lower()
        self.parameters = kwargs

    def log_prior(self, lengthscale: float, variance: float) -> float:
        """
        Compute the log prior for GP hyperparameters.

        Args:
            lengthscale: Length scale parameter
            variance: Variance parameter

        Returns:
            Log prior value
        """
        # Log-normal priors for positive parameters
        ls_mu = self.parameters.get('lengthscale_mu', 0.0)
        ls_sigma = self.parameters.get('lengthscale_sigma', 1.0)
        var_mu = self.parameters.get('variance_mu', 0.0)
        var_sigma = self.parameters.get('variance_sigma', 1.0)

        log_prior = 0.0

        # Length scale prior
        log_prior += -0.5 * ((np.log(lengthscale) - ls_mu) / ls_sigma) ** 2
        log_prior -= np.log(lengthscale * ls_sigma * np.sqrt(2 * np.pi))

        # Variance prior
        log_prior += -0.5 * ((np.log(variance) - var_mu) / var_sigma) ** 2
        log_prior -= np.log(variance * var_sigma * np.sqrt(2 * np.pi))

        return log_prior
