"""
Hierarchical Bayesian models for geospatial applications.

This module provides hierarchical Bayesian models that can handle
multi-level spatial data structures.
"""

import numpy as np
from typing import Dict, Optional, Tuple, Union, Any
from .base import BayesianModel
from ._model_utils import posterior_draw_indices
from ..utils.rng import SeedLike, resolve_rng


class HierarchicalBayesianModel(BayesianModel):
    """
    Hierarchical Bayesian model for multi-level spatial data.

    This model implements a hierarchical structure where observations
    are grouped into levels with shared parameters.
    """

    def __init__(self, n_levels: int = 2, **kwargs: Any):
        """Initialize the hierarchical Bayesian model.

        Args:
            n_levels: Number of hierarchical levels. Each level gets its own
                partially pooled intercept.
            **kwargs: Additional model parameters forwarded to the base class.

        Raises:
            ValueError: If ``n_levels`` is not a positive integer.
        """
        if not isinstance(n_levels, (int, np.integer)) or n_levels < 1:
            raise ValueError("n_levels must be a positive integer")
        # Set before super().__init__, which calls _setup_model and needs this
        # to declare the per-level intercept parameters.
        self.n_levels = int(n_levels)
        self.levels: Dict[str, Any] = {}
        super().__init__(name="HierarchicalBayesianModel", **kwargs)

    def _setup_model(self, **kwargs: Any) -> None:
        """Set up the hierarchical model structure and parameters."""
        # Define parameter distributions for inference
        self.parameters = {
            "mu_alpha": {"prior": "normal", "hyperparams": {"mu": 0.0, "sigma": 10.0}},
            "sigma_alpha": {"prior": "half_normal", "hyperparams": {"sigma": 1.0}},
            "noise": {"prior": "half_normal", "hyperparams": {"sigma": 1.0}},
        }

        # Add level-specific parameters
        for level in range(self.n_levels):
            self.parameters[f"alpha_{level}"] = {
                "prior": "normal",
                "hyperparams": {"mu": "mu_alpha", "sigma": "sigma_alpha"},
            }

    def log_likelihood(self, theta: Dict[str, Any], data: Any) -> float:
        """
        Compute the log-likelihood for the hierarchical model.

        Parameters
        ----------
        theta : dict
            Dictionary of parameter values
        data : dict
            Dictionary with data and grouping structure

        Returns
        -------
        float
            Log-likelihood value
        """
        # Extract data components
        observations = data["observations"]
        groups = data["groups"]

        noise = theta["noise"]

        # Extract level parameters
        alphas = [theta[f"alpha_{level}"] for level in range(self.n_levels)]

        # Compute predictions
        predictions = np.array([alphas[group] for group in groups])

        # Compute log-likelihood assuming Gaussian noise
        residuals = observations - predictions
        log_likelihood = -0.5 * np.sum(
            residuals**2 / noise**2 + np.log(2 * np.pi * noise**2)
        )

        return float(log_likelihood)

    def log_prior(self, theta: Dict[str, Any]) -> float:
        """
        Compute the log-prior for the hierarchical model parameters.

        Parameters
        ----------
        theta : dict
            Dictionary of parameter values

        Returns
        -------
        float
            Log-prior value
        """
        log_prior = 0.0

        # Prior for mu_alpha
        mu_alpha = theta["mu_alpha"]
        mu = self.parameters["mu_alpha"]["hyperparams"]["mu"]
        sigma = self.parameters["mu_alpha"]["hyperparams"]["sigma"]
        log_prior += -0.5 * ((mu_alpha - mu) / sigma) ** 2 - np.log(
            sigma * np.sqrt(2 * np.pi)
        )

        # Prior for sigma_alpha
        sigma_alpha = theta["sigma_alpha"]
        sigma = self.parameters["sigma_alpha"]["hyperparams"]["sigma"]
        log_prior += -np.log(sigma_alpha) - sigma**2 / (2 * sigma_alpha**2)

        # Prior for noise
        noise = theta["noise"]
        sigma = self.parameters["noise"]["hyperparams"]["sigma"]
        log_prior += -np.log(noise) - sigma**2 / (2 * noise**2)

        # Priors for level alphas
        for level in range(self.n_levels):
            alpha = theta[f"alpha_{level}"]
            mu = theta["mu_alpha"]  # mu_alpha is used as mean for level alphas
            sigma = theta["sigma_alpha"]
            log_prior += -0.5 * ((alpha - mu) / sigma) ** 2 - np.log(
                sigma * np.sqrt(2 * np.pi)
            )

        return float(log_prior)

    def predict(
        self,
        X_new: np.ndarray,
        posterior: Any = None,
        samples: int = 100,
        return_std: bool = False,
    ) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
        """
        Make predictions at new locations.

        Parameters
        ----------
        X_new : array-like
            New locations to predict at
        posterior : PosteriorAnalysis, optional
            Posterior analysis object. If None, use current parameters.
        samples : int, default=100
            Number of posterior samples to use
        return_std : bool, default=False
            Whether to return standard deviations

        Returns
        -------
        y_pred : ndarray
            Predictions
        y_std : ndarray, optional
            Standard deviations of predictions
        """
        if posterior is not None:
            # Use posterior samples
            all_preds = []

            names = [f"alpha_{level}" for level in range(self.n_levels)]
            for i in posterior_draw_indices(posterior, samples, names):
                # Extract level parameters
                alphas = [
                    posterior.samples[f"alpha_{level}"][i]
                    for level in range(self.n_levels)
                ]

                # Make predictions for new data
                if hasattr(X_new, "__len__") and len(X_new) > 0:
                    if isinstance(X_new[0], (list, tuple, np.ndarray)):
                        # X_new contains group indices
                        predictions = np.array([alphas[group] for group in X_new])
                    else:
                        # Assume all new points belong to level 0
                        predictions = np.full(len(X_new), alphas[0])
                else:
                    predictions = np.array([alphas[0]])

                all_preds.append(predictions)

            # Compute statistics across samples
            stacked = np.stack(all_preds)
            mean_pred = np.asarray(np.mean(stacked, axis=0), dtype=float)

            if return_std:
                return mean_pred, np.asarray(np.std(stacked, axis=0), dtype=float)
            return mean_pred
        else:
            raise RuntimeError(
                "Direct prediction requires a posterior. Pass a posterior or run fit() first."
            )

    def posterior_predictive(
        self,
        posterior: Any,
        X: Optional[np.ndarray] = None,
        samples: int = 100,
        random_seed: SeedLike = None,
    ) -> np.ndarray:
        """
        Generate posterior predictive samples.

        Parameters
        ----------
        posterior : PosteriorAnalysis
            Posterior analysis object
        X : array-like, optional
            Locations to generate predictions for. If None, use observed locations.
        samples : int, default=100
            Number of posterior samples to use
        random_seed : int or numpy.random.Generator, optional
            Seed or generator for the observation-noise draws. ``None``
            (default) means a generator seeded from OS entropy, so results are
            not replayable; pass an int to replay. See
            :func:`geo_infer_bayes.utils.rng.resolve_rng`.

        Returns
        -------
        ndarray of shape (samples, n_points)
            Posterior predictive samples
        """
        if X is None:
            # Fall back to the group structure seen during fitting.
            X = np.asarray(getattr(self, "observed_groups", []))

        # Get predictions. return_std=True guarantees the tuple form.
        predictions, _std = self.predict(
            np.asarray(X), posterior, samples=samples, return_std=True
        )

        # Generate samples with noise
        rng = resolve_rng(random_seed)

        all_samples = []
        for i in posterior_draw_indices(posterior, samples, ["noise"]):
            # Each draw carries its own observation-noise variance, so the
            # predictive spread widens with posterior uncertainty about noise.
            noise_sample = float(np.asarray(posterior.samples["noise"])[i])
            all_samples.append(rng.normal(predictions, np.sqrt(noise_sample)))

        return np.stack(all_samples)
