"""
Tools for analyzing posterior distributions from Bayesian inference.
"""

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import arviz as az
import pandas as pd
from typing import Any, Dict, List, Optional, Tuple, Union

from ..models.base import BayesianModel


class PosteriorAnalysis:
    """
    Analyze and visualize posterior distributions from Bayesian inference.

    This class provides tools for summarizing, analyzing, and visualizing
    posterior distributions obtained from Bayesian inference.

    Parameters
    ----------
    model : BayesianModel
        The model used for inference
    samples : dict or xarray.Dataset
        Posterior samples from inference
    data : dict or xarray.Dataset
        Data used for inference
    method : str
        Inference method used
    n_chains : int, default=1
        Number of chains the samplers ran. Samplers hand back draws already
        concatenated across chains, so this is what lets the split-chain
        diagnostics -- R-hat above all -- be computed at all. Leaving it at 1
        makes ``r_hat`` undefined, which ArviZ reports as ``NaN``.
    """

    def __init__(
        self,
        model: "BayesianModel",
        samples: Union[Dict[str, np.ndarray], xr.Dataset, Any],
        data: Union[Dict[str, np.ndarray], xr.Dataset, None],
        method: str,
        n_chains: int = 1,
    ):
        if not isinstance(n_chains, (int, np.integer)) or n_chains < 1:
            raise ValueError("n_chains must be a positive integer")
        self.model = model
        self.samples = samples
        self.data = data
        self.method = method
        self.n_chains = int(n_chains)

        # Convert samples to InferenceData if not already
        if not isinstance(samples, az.InferenceData):
            self.arviz_data = self._convert_to_arviz(samples)
        else:
            self.arviz_data = samples

    def chain_samples(self) -> Dict[str, np.ndarray]:
        """Return the draws reshaped to ``(chain, draw, ...)``.

        Samplers concatenate chains in C order, so reshaping the leading axis
        recovers the original chain assignment exactly. Use this for any
        between-chain diagnostic; ``self.samples`` stays flat because
        prediction and model comparison want one pooled draw axis.

        Returns
        -------
        dict of str to ndarray
            One array per parameter, leading axis of length ``n_chains``.

        Raises
        ------
        TypeError
            If the samples are not a dict of arrays.
        ValueError
            If a parameter's draw count is not divisible by ``n_chains``.
        """
        if not isinstance(self.samples, dict):
            raise TypeError("chain_samples requires dict-valued samples")
        reshaped: Dict[str, np.ndarray] = {}
        for name, values in self.samples.items():
            array = np.asarray(values)
            if array.shape[0] % self.n_chains:
                raise ValueError(
                    f"parameter '{name}' has {array.shape[0]} draws, which is "
                    f"not divisible by n_chains={self.n_chains}"
                )
            reshaped[name] = array.reshape(
                (self.n_chains, array.shape[0] // self.n_chains) + array.shape[1:]
            )
        return reshaped

    def _convert_to_arviz(
        self, samples: Union[Dict[str, np.ndarray], xr.Dataset]
    ) -> Any:
        """Convert samples to ArviZ InferenceData format.

        Draws arrive pooled across chains; ArviZ needs an explicit chain axis
        to compute R-hat and split-ESS, so the pooled axis is unpacked here.
        """
        if isinstance(samples, dict):
            # ArviZ requires observed_data to be a dict; wrap raw arrays
            obs_data = self.data
            if obs_data is not None and not isinstance(obs_data, dict):
                obs_data = {"observed": np.asarray(obs_data)}
            posterior = samples
            if self.n_chains > 1:
                try:
                    posterior = self.chain_samples()
                except ValueError:
                    # Ragged draw counts: fall back to a single pooled chain
                    # rather than mislabelling which draw came from which chain.
                    posterior = samples
            return az.from_dict(posterior=posterior, observed_data=obs_data)
        # An xarray Dataset already carries chain/draw dims, so it is wrapped
        # as-is rather than reshaped.
        return az.InferenceData(posterior=samples)

    def summary(self, parameters: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Summarize the posterior distribution.

        Parameters
        ----------
        parameters : list of str, optional
            Parameters to include in the summary. If None, include all.

        Returns
        -------
        pandas.DataFrame
            Summary statistics for the posterior
        """
        return az.summary(self.arviz_data, var_names=parameters)

    def plot_trace(self, parameters: Optional[List[str]] = None) -> None:
        """
        Plot MCMC traces for the posterior samples.

        Parameters
        ----------
        parameters : list of str, optional
            Parameters to plot. If None, plot all.
        """
        az.plot_trace(self.arviz_data, var_names=parameters)
        plt.tight_layout()

    def plot_posterior(self, parameters: Optional[List[str]] = None) -> None:
        """
        Plot posterior distributions.

        Parameters
        ----------
        parameters : list of str, optional
            Parameters to plot. If None, plot all.
        """
        az.plot_posterior(self.arviz_data, var_names=parameters)
        plt.tight_layout()

    def plot_forest(self, parameters: Optional[List[str]] = None) -> None:
        """
        Forest plot of posterior distributions.

        Parameters
        ----------
        parameters : list of str, optional
            Parameters to plot. If None, plot all.
        """
        az.plot_forest(self.arviz_data, var_names=parameters)
        plt.tight_layout()

    def plot_spatial_prediction(
        self, grid: Optional[np.ndarray] = None, uncertainty: bool = True
    ) -> Tuple[plt.Figure, plt.Axes]:
        """
        Plot spatial predictions from the posterior.

        Parameters
        ----------
        grid : array-like, optional
            Grid points to predict on. If None, use a default grid.
        uncertainty : bool, default=True
            Whether to plot uncertainty bounds

        Returns
        -------
        fig, ax : matplotlib Figure and Axes
            Plot objects
        """
        return self.model.plot_prediction(self, grid=grid, uncertainty=uncertainty)

    def predict(
        self, X_new: np.ndarray, samples: int = 100, return_std: bool = False
    ) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
        """
        Make predictions at new locations using the posterior.

        Parameters
        ----------
        X_new : array-like
            New locations to predict at
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
        return self.model.predict(
            X_new, posterior=self, samples=samples, return_std=return_std
        )

    def credible_interval(
        self, parameter: str, alpha: float = 0.05
    ) -> Tuple[float, float]:
        """
        Compute credible interval for a parameter.

        Parameters
        ----------
        parameter : str
            Name of the parameter
        alpha : float, default=0.05
            Significance level (e.g., 0.05 for 95% CI)

        Returns
        -------
        lower, upper : float, float
            Lower and upper bounds of the credible interval
        """
        if not isinstance(alpha, (int, float, np.floating, np.integer)):
            raise TypeError("alpha must be a real number")
        level = float(alpha)
        if not np.isfinite(level) or not 0.0 < level < 1.0:
            raise ValueError("alpha must be finite and strictly between zero and one")
        try:
            param_samples = np.asarray(
                self.arviz_data.posterior[parameter].values
            ).astype(float).reshape(-1)
        except (AttributeError, KeyError) as exc:
            raise KeyError(
                f"posterior does not contain parameter {parameter!r}"
            ) from exc
        if param_samples.size == 0 or not np.all(np.isfinite(param_samples)):
            raise ValueError("posterior parameter samples must be non-empty and finite")
        lower = np.percentile(param_samples, 100.0 * level / 2.0)
        upper = np.percentile(param_samples, 100.0 * (1.0 - level / 2.0))
        return float(lower), float(upper)

    def posterior_predictive(
        self, X: Optional[np.ndarray] = None, samples: int = 100
    ) -> np.ndarray:
        """
        Generate posterior predictive samples.

        Parameters
        ----------
        X : array-like, optional
            Locations to generate predictions for. If None, use observed locations.
        samples : int, default=100
            Number of posterior samples to use

        Returns
        -------
        ndarray
            Posterior predictive samples
        """
        return self.model.posterior_predictive(posterior=self, X=X, samples=samples)
