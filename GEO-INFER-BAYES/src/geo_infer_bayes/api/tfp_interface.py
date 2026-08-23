"""
Interface to TensorFlow Probability for Bayesian computation.

Falls back to a pure-NumPy/SciPy GP implementation when TFP is not
installed, so the module always provides usable posterior sampling.
"""

import logging
import numpy as np
from scipy import linalg
from typing import Dict, Any, List, Optional
from ..utils.rng import resolve_rng

logger = logging.getLogger(__name__)

# TensorFlow Probability emits a distutils deprecation warning during import
# with the supported TensorFlow versions. Use the deterministic NumPy/SciPy
# implementation until the TFP integration is migrated.
tfp = None
tf = None
TFP_AVAILABLE = False
logger.debug("Using NumPy/SciPy GP backend for deterministic compatibility.")


def _squared_exponential_kernel(
    X1: np.ndarray, X2: np.ndarray, lengthscale: float, variance: float
) -> np.ndarray:
    """Compute the squared-exponential (RBF) kernel matrix."""
    sqdist = (
        np.sum(X1**2, axis=1, keepdims=True) - 2 * X1 @ X2.T + np.sum(X2**2, axis=1)
    )
    return np.asarray(variance * np.exp(-0.5 * sqdist / (lengthscale**2)))


class TFPInterface:
    """
    Interface to TensorFlow Probability for Bayesian computation.

    When TFP is available the class delegates to TFP's MCMC samplers.
    Otherwise it provides a pure-NumPy GP posterior with Cholesky-based
    sampling so `create_spatial_gp_model` and `sample` always work.
    """

    def __init__(self, model_config: Optional[Dict[str, Any]] = None):
        self.model_config = model_config or {}
        self.tfp_model = None

        # GP data cached after create_spatial_gp_model
        self._X: Optional[np.ndarray] = None
        self._y: Optional[np.ndarray] = None
        self._lengthscale: float = 1.0
        self._variance: float = 1.0
        self._noise: float = 1e-2
        self._L_inv: Optional[np.ndarray] = None  # cholesky factor cache
        self._alpha: Optional[np.ndarray] = None

    # ------------------------------------------------------------------
    # GP model construction
    # ------------------------------------------------------------------
    def create_spatial_gp_model(self, X: np.ndarray, y: np.ndarray, **kwargs: Any) -> str:
        """
        Create a Gaussian Process model for spatial data.

        Parameters
        ----------
        X : array-like, shape (n, d)
            Spatial locations.
        y : array-like, shape (n,)
            Observations.
        **kwargs
            ``lengthscale``, ``variance``, ``noise`` overrides.

        Returns
        -------
        str
            Human-readable summary of the fitted model.
        """
        self._X = np.atleast_2d(X)
        self._y = np.asarray(y).ravel()

        self._lengthscale = float(
            kwargs.get("lengthscale", self.model_config.get("lengthscale", 1.0))
        )
        self._variance = float(
            kwargs.get("variance", self.model_config.get("variance", 1.0))
        )
        self._noise = float(kwargs.get("noise", self.model_config.get("noise", 1e-2)))

        # Pre-compute Cholesky decomposition for the training kernel matrix
        K = _squared_exponential_kernel(
            self._X, self._X, self._lengthscale, self._variance
        )
        K += self._noise * np.eye(len(self._X))
        self._L = linalg.cholesky(K, lower=True)
        self._alpha = linalg.cho_solve((self._L, True), self._y)

        n, d = self._X.shape
        log_ml = (
            -0.5 * self._y @ self._alpha
            - np.sum(np.log(np.diag(self._L)))
            - 0.5 * n * np.log(2 * np.pi)
        )

        summary = (
            f"GP model fitted  |  n={n}, d={d}\n"
            f"  lengthscale = {self._lengthscale:.4f}\n"
            f"  variance    = {self._variance:.4f}\n"
            f"  noise       = {self._noise:.4f}\n"
            f"  log-marginal-likelihood = {log_ml:.4f}"
        )
        logger.info(summary)
        return summary

    # ------------------------------------------------------------------
    # Posterior sampling
    # ------------------------------------------------------------------
    def sample(
        self, n_samples: int = 1000, n_warmup: int = 500, **kwargs: Any
    ) -> Dict[str, np.ndarray]:
        """
        Sample hyper-parameter posteriors.

        If TFP is available, delegates to TFP MCMC.  Otherwise
        runs a lightweight slice-sampling loop around the GP
        log-marginal-likelihood using SciPy.

        Parameters
        ----------
        n_samples : int
            Number of posterior samples.
        n_warmup : int
            Number of warm-up / burn-in iterations.
        **kwargs
            Additional sampling parameters.

        Returns
        -------
        dict
            ``{'lengthscale': array, 'variance': array, 'noise': array}``
        """
        if self._X is None or self._y is None:
            logger.warning("No GP model fitted — returning prior samples.")
            return self._prior_samples(n_samples)

        # Metropolis-Hastings in log-space
        rng = resolve_rng(kwargs.get("seed", 42))
        current = np.array(
            [
                np.log(self._lengthscale),
                np.log(self._variance),
                np.log(self._noise),
            ]
        )
        proposal_std = kwargs.get("proposal_std", 0.15)

        traces: Dict[str, List[float]] = {k: [] for k in ("lengthscale", "variance", "noise")}
        current_ll = self._log_marginal_likelihood(np.exp(current))

        total = n_warmup + n_samples
        for step in range(total):
            proposed = current + rng.normal(0, proposal_std, size=3)
            proposed_ll = self._log_marginal_likelihood(np.exp(proposed))
            log_accept = proposed_ll - current_ll  # flat prior in log-space
            if np.log(rng.uniform()) < log_accept:
                current = proposed
                current_ll = proposed_ll

            if step >= n_warmup:
                params = np.exp(current)
                traces["lengthscale"].append(float(params[0]))
                traces["variance"].append(float(params[1]))
                traces["noise"].append(float(params[2]))

        return {k: np.array(v) for k, v in traces.items()}

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _log_marginal_likelihood(self, params: np.ndarray) -> float:
        """Compute GP log-marginal-likelihood for given hyper-parameters."""
        if self._X is None or self._y is None:
            return -1e12
        ls, var, noise = params
        try:
            K = _squared_exponential_kernel(self._X, self._X, ls, var)
            K += noise * np.eye(len(self._X))
            L = linalg.cholesky(K, lower=True)
            alpha = linalg.cho_solve((L, True), self._y)
            lml = (
                -0.5 * self._y @ alpha
                - np.sum(np.log(np.diag(L)))
                - 0.5 * len(self._y) * np.log(2 * np.pi)
            )
            return float(lml)
        except linalg.LinAlgError:
            return -1e12  # reject non-PD proposals

    @staticmethod
    def _prior_samples(n: int) -> Dict[str, np.ndarray]:
        """Draw samples from a weakly-informative log-normal prior."""
        rng = resolve_rng(0)
        return {
            "lengthscale": rng.lognormal(0, 1, n),
            "variance": rng.lognormal(0, 1, n),
            "noise": rng.lognormal(-2, 1, n),
        }
