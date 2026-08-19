"""
Gaussian Process model for spatial data.
"""

from contextlib import contextmanager
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple, Union

import numpy as np
from scipy.spatial.distance import cdist
from scipy.linalg import cholesky, solve_triangular

from .base import BayesianModel
from ._model_utils import posterior_draw_indices
from ..utils.rng import SeedLike, resolve_rng


class SpatialGP(BayesianModel):
    """
    Gaussian Process model for spatial data.

    This class implements a Gaussian Process regression model
    for spatial interpolation and prediction.

    Parameters
    ----------
    kernel : str, default='matern'
        Covariance kernel: 'matern', 'rbf', 'exponential'
    lengthscale : float, default=1.0
        Length scale parameter for the kernel
    variance : float, default=1.0
        Variance parameter for the kernel
    noise : float, default=0.1
        Observation noise variance
    degree : float, default=1.5
        Degree parameter for the Matern kernel
    mean_function : callable, optional
        Mean function for the GP
    jitter : float, default=1e-6
        Small value added to the diagonal for numerical stability
    """

    def __init__(
        self,
        kernel: str = "matern",
        lengthscale: float = 1.0,
        variance: float = 1.0,
        noise: float = 0.1,
        degree: float = 1.5,
        mean_function: Optional[Callable[[np.ndarray], np.ndarray]] = None,
        jitter: float = 1e-6,
        **kwargs: Any,
    ) -> None:
        self.kernel_type = kernel.lower()
        self.lengthscale = lengthscale
        self.variance = variance
        self.noise = noise
        self.degree = degree
        self.mean_function = mean_function or (lambda x: np.zeros(len(x)))
        self.jitter = jitter
        # None until fit(); every method that needs them checks first.
        self.X_train: Optional[np.ndarray] = None
        self.y_train: Optional[np.ndarray] = None
        self.L: Optional[np.ndarray] = None  # Cholesky factor of the covariance

        super().__init__(name="SpatialGP", **kwargs)

    def _setup_model(self, **kwargs: Any) -> None:
        """Set up the Gaussian Process model."""
        # Define parameter distributions for inference
        self.parameters = {
            "lengthscale": {
                "prior": "log_normal",
                "hyperparams": {"mu": 0.0, "sigma": 1.0},
            },
            "variance": {
                "prior": "log_normal",
                "hyperparams": {"mu": 0.0, "sigma": 1.0},
            },
            "noise": {"prior": "log_normal", "hyperparams": {"mu": -2.0, "sigma": 1.0}},
        }

        if self.kernel_type == "matern":
            self.parameters["degree"] = {
                "prior": "uniform",
                "hyperparams": {"low": 0.5, "high": 3.0},
            }

        # Initialize kernels based on type
        self.kernel_fn = self._get_kernel_function()

    def _get_kernel_function(self) -> Callable:
        """Get the appropriate kernel function based on the kernel type."""
        if self.kernel_type == "rbf":
            return self._rbf_kernel
        elif self.kernel_type == "matern":
            return self._matern_kernel
        elif self.kernel_type == "exponential":
            return self._exponential_kernel
        else:
            raise ValueError(f"Unknown kernel type: {self.kernel_type}")

    def _rbf_kernel(self, X1: np.ndarray, X2: np.ndarray) -> np.ndarray:
        """RBF (squared exponential) kernel."""
        dist = cdist(X1, X2)
        return np.asarray(
            self.variance * np.exp(-0.5 * (dist / self.lengthscale) ** 2), dtype=float
        )

    def _matern_kernel(self, X1: np.ndarray, X2: np.ndarray) -> np.ndarray:
        """Matern kernel with adjustable degree."""
        dist = cdist(X1, X2)

        if self.degree == 0.5:
            # Exponential kernel
            kernel = self.variance * np.exp(-dist / self.lengthscale)
        elif self.degree == 1.5:
            # Matern 3/2
            scaled_dist = np.sqrt(3) * dist / self.lengthscale
            kernel = self.variance * (1 + scaled_dist) * np.exp(-scaled_dist)
        elif self.degree == 2.5:
            # Matern 5/2
            scaled_dist = np.sqrt(5) * dist / self.lengthscale
            kernel = (
                self.variance
                * (1 + scaled_dist + scaled_dist**2 / 3)
                * np.exp(-scaled_dist)
            )
        else:
            # Other degrees fall back to a stretched-exponential form, which is
            # not a Matern kernel; only the three cases above are exact.
            scaled_dist = dist / self.lengthscale
            kernel = self.variance * np.exp(-(scaled_dist**self.degree))
        return np.asarray(kernel, dtype=float)

    def _exponential_kernel(self, X1: np.ndarray, X2: np.ndarray) -> np.ndarray:
        """Exponential kernel."""
        dist = cdist(X1, X2)
        return np.asarray(self.variance * np.exp(-dist / self.lengthscale), dtype=float)

    def fit(self, X: np.ndarray, y: np.ndarray) -> "SpatialGP":
        """
        Fit the GP to training data.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training input samples
        y : array-like of shape (n_samples,)
            Target values

        Returns
        -------
        self : object
            Returns self
        """
        self.X_train = np.asarray(X)
        self.y_train = np.asarray(y)

        # Compute covariance matrix
        K = self.kernel_fn(self.X_train, self.X_train)
        K += np.eye(len(self.X_train)) * (self.noise + self.jitter)

        # Cache Cholesky factor for predictions
        self.L = cholesky(K, lower=True)

        return self

    def _posterior_draws(self, posterior: Any, samples: int) -> List[Dict[str, float]]:
        """Return hyperparameter dicts for the draws a prediction averages over.

        Parameters
        ----------
        posterior : PosteriorAnalysis
            Posterior holding the sampled hyperparameters.
        samples : int
            Maximum number of draws to use.

        Returns
        -------
        list of dict
            One parameter dict per selected draw, spread evenly across the
            chain.
        """
        names = ["lengthscale", "variance", "noise"]
        if self.kernel_type == "matern":
            names.append("degree")
        indices = posterior_draw_indices(posterior, samples, names)
        return [
            {name: float(np.asarray(posterior.samples[name])[i]) for name in names}
            for i in indices
        ]

    @contextmanager
    def _parameters_from(self, theta: Dict[str, Any]) -> Iterator[None]:
        """Adopt hyperparameters from ``theta`` without touching cached state.

        Unlike :meth:`_temporary_parameters` this does not refactorize the
        training covariance, so it is the right tool for evaluating a likelihood
        on data other than the training set.

        Parameters
        ----------
        theta : dict
            Hyperparameter values to adopt; unknown keys are ignored.

        Yields
        ------
        None
        """
        tracked = ("lengthscale", "variance", "noise", "degree", "kernel_type")
        saved = {name: getattr(self, name) for name in tracked}
        saved_kernel = self.kernel_fn
        try:
            for name in tracked:
                if name in theta:
                    setattr(self, name, theta[name])
            self.kernel_fn = self._get_kernel_function()
            yield
        finally:
            for name, value in saved.items():
                setattr(self, name, value)
            self.kernel_fn = saved_kernel

    @contextmanager
    def _temporary_parameters(self, theta: Dict[str, float]) -> Iterator[None]:
        """Adopt one hyperparameter draw, then restore the fitted state.

        Refactorizing the training covariance is what makes the draw usable:
        the Cholesky factor cached by :meth:`fit` belongs to the fitted
        hyperparameters, not to ``theta``. The original factor and parameters
        are restored even if the body raises, so a failed draw cannot leave the
        model describing a covariance it no longer holds.

        Parameters
        ----------
        theta : dict
            Hyperparameter values to adopt; unknown keys are ignored.

        Yields
        ------
        None
        """
        X_train, _, _ = self._fitted_state()
        tracked = ("lengthscale", "variance", "noise", "degree")
        saved = {name: getattr(self, name) for name in tracked}
        saved_L, saved_kernel = self.L, self.kernel_fn
        try:
            for name in tracked:
                if name in theta:
                    setattr(self, name, theta[name])
            self.kernel_fn = self._get_kernel_function()
            K = self.kernel_fn(X_train, X_train)
            K += np.eye(len(X_train)) * (self.noise + self.jitter)
            self.L = cholesky(K, lower=True)
            yield
        finally:
            for name, value in saved.items():
                setattr(self, name, value)
            self.L, self.kernel_fn = saved_L, saved_kernel

    def bind_training_data(self, data: Any) -> None:
        """Fit the GP to the data inference conditioned on.

        A GP predictive distribution is defined only relative to its training
        set, so sampling hyperparameters is not enough: the Cholesky factor of
        the training covariance has to exist before
        :meth:`predict` can be called with a posterior.

        Parameters
        ----------
        data : dict
            Prepared data holding ``X`` and ``y``. Anything else is ignored, so
            a model conditioned on a different data shape still runs.
        """
        if isinstance(data, dict) and "X" in data and "y" in data:
            self.fit(data["X"], data["y"])

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
            Posterior analysis object. If None, use current GP parameters.
        samples : int, default=100
            Number of posterior samples to use if posterior is provided
        return_std : bool, default=False
            Whether to return standard deviations

        Returns
        -------
        y_pred : ndarray
            Predicted mean
        y_std : ndarray, optional
            Predicted standard deviation
        """
        X_new = np.asarray(X_new)

        if posterior is not None:
            if self.X_train is None or self.y_train is None:
                raise ValueError(
                    "Model has not been fitted. Call fit() before posterior prediction."
                )

            means = []
            conditional_variances = []
            for theta in self._posterior_draws(posterior, samples):
                with self._temporary_parameters(theta):
                    if return_std:
                        mean, std = self._conditional_mean_std(X_new)
                        conditional_variances.append(std**2)
                    else:
                        mean = self._conditional_mean(X_new)
                means.append(mean)

            stacked = np.stack(means)
            mean_pred = np.asarray(np.mean(stacked, axis=0), dtype=float)

            if return_std:
                # Law of total variance. The spread of the per-draw means alone
                # captures only hyperparameter uncertainty and understates the
                # predictive interval badly -- for a well-identified posterior
                # the conditional GP variance is the dominant term.
                total_variance = np.mean(
                    np.stack(conditional_variances), axis=0
                ) + np.var(stacked, axis=0)
                return mean_pred, np.asarray(np.sqrt(total_variance), dtype=float)
            return mean_pred

        # No posterior: predict at the currently held hyperparameters.
        if return_std:
            return self._conditional_mean_std(X_new)
        return self._conditional_mean(X_new)

    def _fitted_state(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Return the training inputs, targets and Cholesky factor.

        Returns
        -------
        tuple of ndarray
            ``(X_train, y_train, L)``.

        Raises
        ------
        ValueError
            If the model has not been fitted.
        """
        if self.X_train is None or self.y_train is None or self.L is None:
            raise ValueError("Model has not been fitted. Call fit() first.")
        return self.X_train, self.y_train, self.L

    def _conditional_mean(self, X_new: np.ndarray) -> np.ndarray:
        """Posterior mean of the latent function at ``X_new``.

        Parameters
        ----------
        X_new : ndarray
            Locations to predict at.

        Returns
        -------
        ndarray
            Posterior mean, one entry per row of ``X_new``.
        """
        X_train, y_train, L = self._fitted_state()
        K_s = self.kernel_fn(X_train, X_new)
        alpha = solve_triangular(L, y_train - self.mean_function(X_train), lower=True)
        alpha = solve_triangular(L.T, alpha, lower=False)
        return np.asarray(self.mean_function(X_new) + K_s.T @ alpha, dtype=float)

    def _conditional_mean_std(
        self, X_new: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Posterior mean and standard deviation of the latent function.

        The standard deviation excludes observation noise, which belongs to a
        predictive draw rather than to the latent function; see
        :meth:`posterior_predictive`.

        Parameters
        ----------
        X_new : ndarray
            Locations to predict at.

        Returns
        -------
        tuple of ndarray
            ``(mean, std)``, each with one entry per row of ``X_new``.
        """
        X_train, _, L = self._fitted_state()
        mean = self._conditional_mean(X_new)
        K_s = self.kernel_fn(X_train, X_new)
        v = solve_triangular(L, K_s, lower=True)
        K_ss = self.kernel_fn(X_new, X_new)
        # Clipped at the jitter: the exact expression can go slightly negative
        # from rounding when a prediction point coincides with a training point.
        var = np.clip(np.diag(K_ss - v.T @ v), self.jitter, np.inf)
        return mean, np.asarray(np.sqrt(var), dtype=float)

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
            not replayable; pass an int to replay, or a ``Generator`` to thread
            one stream through a pipeline. See
            :func:`geo_infer_bayes.utils.rng.resolve_rng`.

        Returns
        -------
        ndarray of shape (samples, n_points)
            Posterior predictive samples
        """
        rng = resolve_rng(random_seed)

        if X is None:
            X = self.X_train

        X = np.asarray(X)
        if self.X_train is None or self.y_train is None:
            raise ValueError(
                "Model has not been fitted. Call fit() before posterior prediction."
            )
        all_samples = []
        for theta in self._posterior_draws(posterior, samples):
            with self._temporary_parameters(theta):
                mean, std = self._conditional_mean_std(X)
            # std is the latent-function uncertainty; a predictive draw of an
            # observation also carries the observation-noise variance.
            all_samples.append(
                rng.normal(mean, np.sqrt(std**2 + theta["noise"]))
            )

        if not all_samples:
            raise ValueError("posterior contains no usable parameter samples")
        return np.stack(all_samples)

    def log_likelihood(
        self, theta: Dict[str, Any], data: Dict[str, np.ndarray]
    ) -> float:
        """
        Compute the marginal log-likelihood of the GP.

        Parameters
        ----------
        theta : dict
            Dictionary of parameter values
        data : dict
            Dictionary with 'X' and 'y' keys

        Returns
        -------
        float
            Log-likelihood value
        """
        X, y = data["X"], data["y"]

        # Set parameters from theta
        old_params = {}
        for param in ["lengthscale", "variance", "noise", "degree"]:
            if param in theta:
                old_params[param] = getattr(self, param)
                setattr(self, param, theta[param])

        # Update kernel function if needed
        if "kernel_type" in theta:
            old_params["kernel_type"] = self.kernel_type
            self.kernel_type = theta["kernel_type"]
            self.kernel_fn = self._get_kernel_function()

        # Compute kernel matrix
        K = self.kernel_fn(X, X)
        K += np.eye(len(X)) * (self.noise + self.jitter)

        # Compute log likelihood
        try:
            L = cholesky(K, lower=True)
            alpha = solve_triangular(L, y - self.mean_function(X), lower=True)
            alpha = solve_triangular(L.T, alpha, lower=False)

            # Marginalized log likelihood
            log_likelihood = -0.5 * np.dot(y - self.mean_function(X), alpha)
            log_likelihood -= np.sum(np.log(np.diag(L)))
            log_likelihood -= 0.5 * len(X) * np.log(2 * np.pi)
        except np.linalg.LinAlgError:
            log_likelihood = -np.inf

        # Restore parameters
        for param, value in old_params.items():
            setattr(self, param, value)
        if "kernel_type" in old_params:
            self.kernel_fn = self._get_kernel_function()

        return float(log_likelihood)

    def pointwise_log_likelihood(
        self, theta: Dict[str, Any], data: Dict[str, np.ndarray]
    ) -> np.ndarray:
        """Decompose the GP marginal log-likelihood into per-observation terms.

        LOO and WAIC need a log-likelihood per observation, but a GP likelihood
        is joint, not factorized. The usable decomposition is the ordered
        conditional one: with ``K = L L^T`` and ``z = L^{-1} (y - m)``,

            log p(y_i | y_1..y_{i-1}) = -z_i^2 / 2 - log L_ii - log(2 pi) / 2

        and those terms sum exactly to the joint marginal log-likelihood. Naive
        alternatives are wrong in a way that is easy to miss: evaluating each
        point's own marginal density drops all correlation, and for a stationary
        kernel it drops the kernel entirely -- ``K(x, x)`` equals the signal
        variance whatever the lengthscale -- so every kernel scores identically.

        Parameters
        ----------
        theta : dict
            Hyperparameter values to evaluate at.
        data : dict
            Dictionary with ``X`` and ``y`` keys.

        Returns
        -------
        ndarray of shape (n_obs,)
            Per-observation log-likelihood contributions, summing to
            :meth:`log_likelihood`. All ``-inf`` if the covariance is not
            positive definite at ``theta``.

        Notes
        -----
        The decomposition depends on the observation order, though its sum does
        not. Diagnostics that treat the terms as exchangeable, Pareto-k among
        them, inherit that dependence.
        """
        X = np.asarray(data["X"], dtype=float)
        y = np.asarray(data["y"], dtype=float)

        with self._parameters_from(theta):
            K = self.kernel_fn(X, X)
            K += np.eye(len(X)) * (self.noise + self.jitter)
            try:
                L = cholesky(K, lower=True)
            except np.linalg.LinAlgError:
                return np.full(len(X), -np.inf)
            z = solve_triangular(L, y - self.mean_function(X), lower=True)

        return np.asarray(
            -0.5 * z**2 - np.log(np.diag(L)) - 0.5 * np.log(2 * np.pi), dtype=float
        )

    def log_prior(self, theta: Dict[str, Any]) -> float:
        """
        Compute the log-prior for the GP parameters.

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

        # Log-normal prior for lengthscale
        if "lengthscale" in theta:
            mu = self.parameters["lengthscale"]["hyperparams"]["mu"]
            sigma = self.parameters["lengthscale"]["hyperparams"]["sigma"]
            log_prior += -0.5 * ((np.log(theta["lengthscale"]) - mu) / sigma) ** 2
            log_prior -= np.log(theta["lengthscale"] * sigma * np.sqrt(2 * np.pi))

        # Log-normal prior for variance
        if "variance" in theta:
            mu = self.parameters["variance"]["hyperparams"]["mu"]
            sigma = self.parameters["variance"]["hyperparams"]["sigma"]
            log_prior += -0.5 * ((np.log(theta["variance"]) - mu) / sigma) ** 2
            log_prior -= np.log(theta["variance"] * sigma * np.sqrt(2 * np.pi))

        # Log-normal prior for noise
        if "noise" in theta:
            mu = self.parameters["noise"]["hyperparams"]["mu"]
            sigma = self.parameters["noise"]["hyperparams"]["sigma"]
            log_prior += -0.5 * ((np.log(theta["noise"]) - mu) / sigma) ** 2
            log_prior -= np.log(theta["noise"] * sigma * np.sqrt(2 * np.pi))

        # Uniform prior for degree (if Matern)
        if "degree" in theta and self.kernel_type == "matern":
            low = self.parameters["degree"]["hyperparams"]["low"]
            high = self.parameters["degree"]["hyperparams"]["high"]
            if theta["degree"] < low or theta["degree"] > high:
                log_prior = -np.inf
            else:
                log_prior += -np.log(high - low)

        return log_prior
