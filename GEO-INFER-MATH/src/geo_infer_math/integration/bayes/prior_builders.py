"""Prior distribution builders for Bayesian inference.

Creates properly normalised prior distributions for use in Bayesian
spatial analysis: uniform, normal, beta, gamma, and Dirichlet.
"""

import numpy as np
from typing import Optional, Dict, Any, cast
import logging

logger = logging.getLogger(__name__)


class PriorBuilders:
    """Prior distribution builders for Bayesian inference.

    Provides methods to construct properly normalised prior
    distributions with input validation.
    """

    def __init__(self, epsilon: float = 1e-16) -> None:
        """Initialize prior builder.

        Args:
            epsilon: Numerical stability constant.
        """
        self._epsilon = epsilon
        logger.debug("PriorBuilders initialized")

    def build_prior(
        self,
        prior_type: str,
        size: int = 10,
        **kwargs: Any,
    ) -> np.ndarray:
        """Build a prior distribution.

        Args:
            prior_type: Distribution type — 'uniform', 'normal',
                'beta', 'gamma', 'dirichlet', 'informative'.
            size: Number of elements in the discrete distribution.
            **kwargs: Distribution-specific parameters:
                - normal: 'mean', 'std'
                - beta: 'alpha', 'beta_param'
                - gamma: 'alpha', 'beta_param'
                - dirichlet: 'alpha_vector' or 'concentration'
                - informative: 'peaks' (list of (index, weight) tuples)

        Returns:
            Normalised prior distribution, shape (size,).
        """
        if size < 1:
            raise ValueError(f"Size must be ≥ 1, got {size}")

        if prior_type == "uniform":
            prior = self._uniform(size)
        elif prior_type == "normal":
            prior = self._normal(size, **kwargs)
        elif prior_type == "beta":
            prior = self._beta(size, **kwargs)
        elif prior_type == "gamma":
            prior = self._gamma(size, **kwargs)
        elif prior_type == "dirichlet":
            prior = self._dirichlet(size, **kwargs)
        elif prior_type == "informative":
            prior = self._informative(size, **kwargs)
        else:
            raise ValueError(f"Unknown prior_type: {prior_type}")

        # Ensure normalisation
        prior = prior / (prior.sum() + self._epsilon)

        logger.debug("Built %s prior (size=%d, entropy=%.4f)", prior_type, size, self._entropy(prior))
        return cast(np.ndarray, prior)

    def _uniform(self, size: int) -> np.ndarray:
        """Uniform (maximum entropy) prior."""
        return np.ones(size) / size

    def _normal(self, size: int, **kwargs: Any) -> np.ndarray:
        """Discretised normal distribution."""
        mean = kwargs.get("mean", size / 2)
        std = kwargs.get("std", size / 6)
        x = np.arange(size, dtype=np.float64)
        prior = np.exp(-0.5 * ((x - mean) / (std + self._epsilon)) ** 2)
        return cast(np.ndarray, prior)

    def _beta(self, size: int, **kwargs: Any) -> np.ndarray:
        """Discretised beta distribution."""
        alpha = kwargs.get("alpha", 2.0)
        beta_param = kwargs.get("beta_param", 2.0)
        x = np.linspace(self._epsilon, 1.0 - self._epsilon, size)
        prior = x ** (alpha - 1) * (1 - x) ** (beta_param - 1)
        return cast(np.ndarray, prior)

    def _gamma(self, size: int, **kwargs: Any) -> np.ndarray:
        """Discretised gamma distribution."""
        alpha = kwargs.get("alpha", 2.0)
        beta_param = kwargs.get("beta_param", 1.0)
        x = np.linspace(self._epsilon, size, size)
        prior = x ** (alpha - 1) * np.exp(-beta_param * x)
        return cast(np.ndarray, prior)

    def _dirichlet(self, size: int, **kwargs: Any) -> np.ndarray:
        """Sample from Dirichlet distribution (single draw)."""
        alpha_vector = kwargs.get("alpha_vector", None)
        concentration = kwargs.get("concentration", 1.0)

        if alpha_vector is not None:
            alpha = np.asarray(alpha_vector, dtype=np.float64)
            if len(alpha) != size:
                raise ValueError(f"alpha_vector length ({len(alpha)}) != size ({size})")
        else:
            alpha = np.full(size, concentration)

        # Use the mean of the Dirichlet: α_i / sum(α)
        prior = alpha / alpha.sum()
        return cast(np.ndarray, prior)

    def _informative(self, size: int, **kwargs: Any) -> np.ndarray:
        """Informative prior with specified peaks."""
        peaks = kwargs.get("peaks", [(size // 2, 5.0)])
        prior = np.ones(size)

        for idx, weight in peaks:
            if 0 <= idx < size:
                prior[idx] = weight

        return prior

    def _entropy(self, p: np.ndarray) -> float:
        """Shannon entropy H(p)."""
        p_safe = p + self._epsilon
        return float(-np.sum(p_safe * np.log(p_safe)))
