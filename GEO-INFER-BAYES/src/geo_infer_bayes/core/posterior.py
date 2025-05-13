"""
Tools for analyzing posterior distributions from Bayesian inference.
"""

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import arviz as az
import pandas as pd
from typing import Dict, Any, Optional, Union, List, Tuple, Callable

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
    """
    
    def __init__(
        self, 
        model: 'BayesianModel',
        samples: Union[Dict[str, np.ndarray], xr.Dataset],
        data: Union[Dict[str, np.ndarray], xr.Dataset],
        method: str
    ):
        self.model = model
        self.samples = samples
        self.data = data
        self.method = method
        
        # Convert samples to InferenceData if not already
        if not isinstance(samples, az.InferenceData):
            self.arviz_data = self._convert_to_arviz(samples)
        else:
            self.arviz_data = samples
    
    def _convert_to_arviz(
        self, 
        samples: Union[Dict[str, np.ndarray], xr.Dataset]
    ) -> az.InferenceData:
        """Convert samples to ArviZ InferenceData format."""
        if isinstance(samples, dict):
            return az.from_dict(posterior=samples, observed_data=self.data)
        else:
            return az.from_xarray(posterior=samples)
    
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
        self, 
        grid: Optional[np.ndarray] = None,
        uncertainty: bool = True
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
        self, 
        X_new: np.ndarray,
        samples: int = 100,
        return_std: bool = False
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
            X_new, 
            posterior=self, 
            samples=samples, 
            return_std=return_std
        )
    
    def credible_interval(
        self, 
        parameter: str, 
        alpha: float = 0.05
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
        param_samples = self.arviz_data.posterior[parameter].values.flatten()
        lower = np.percentile(param_samples, 100 * alpha / 2)
        upper = np.percentile(param_samples, 100 * (1 - alpha / 2))
        return lower, upper
    
    def posterior_predictive(
        self, 
        X: Optional[np.ndarray] = None,
        samples: int = 100
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
        return self.model.posterior_predictive(
            posterior=self, 
            X=X, 
            samples=samples
        ) 