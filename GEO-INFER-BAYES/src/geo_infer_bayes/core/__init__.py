"""Core functionality for Bayesian inference."""

# Inference engines
from .inference import BayesianInference
from .posterior import PosteriorAnalysis
from .model_comparison import ModelComparison

# MCMC and computational methods
from .mcmc import MCMC
from .hmc import HMC
from .variational import VariationalInference
from .smc import SequentialMonteCarlo
from .abc import ApproximateBayesianComputation

# Distributional evaluation metrics
from .evaluation import (
    coverage_calibration_error,
    crps,
    crps_gaussian,
    crps_pointwise,
    empirical_coverage,
    evaluate_gaussian,
    evaluate_predictive,
    interval_score,
    log_predictive_density,
    log_predictive_density_gaussian,
    log_predictive_density_pointwise,
    pinball_loss,
    pit_gaussian,
    pit_uniformity_statistic,
    pit_values,
)

__all__ = [
    "BayesianInference",
    "PosteriorAnalysis",
    "ModelComparison",
    "MCMC",
    "HMC",
    "VariationalInference",
    "SequentialMonteCarlo",
    "ApproximateBayesianComputation",
    "crps",
    "crps_pointwise",
    "crps_gaussian",
    "pinball_loss",
    "empirical_coverage",
    "coverage_calibration_error",
    "interval_score",
    "pit_values",
    "pit_gaussian",
    "pit_uniformity_statistic",
    "log_predictive_density",
    "log_predictive_density_pointwise",
    "log_predictive_density_gaussian",
    "evaluate_predictive",
    "evaluate_gaussian",
]
