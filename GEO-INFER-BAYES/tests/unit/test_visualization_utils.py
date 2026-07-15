"""Regression tests for Bayesian visualization contracts."""

import matplotlib.pyplot as plt
import numpy as np
import pytest

from geo_infer_bayes.utils.visualization import (
    plot_model_comparison,
    plot_posterior,
    plot_spatial_prediction,
    plot_uncertainty,
)


def test_spatial_prediction_supports_single_panel_without_uncertainty():
    figure = plot_spatial_prediction(
        np.array([[0.0, 1.0], [1.0, 2.0]]), np.array([0.2, 0.8])
    )
    assert len(figure.axes) == 2  # plot axis and its colorbar
    plt.close(figure)


def test_bayesian_plot_inputs_are_validated():
    with pytest.raises(ValueError, match="same length"):
        plot_spatial_prediction(np.zeros((2, 2)), np.ones(3))
    with pytest.raises(ValueError, match="confidence_level"):
        plot_uncertainty(np.ones(2), np.ones(2), confidence_level=1.0)
    with pytest.raises(ValueError, match="one value per model"):
        plot_model_comparison(["a", "b"], {"rmse": [1.0]})
    with pytest.raises(ValueError, match="at least one"):
        plot_posterior({})


def test_posterior_and_comparison_figures_are_returned():
    posterior = plot_posterior({"theta": np.array([0.1, 0.2, 0.3])})
    comparison = plot_model_comparison(["a", "b"], {"rmse": [1.0, 0.8]})
    assert posterior is not None
    assert comparison is not None
    plt.close(posterior)
    plt.close(comparison)
