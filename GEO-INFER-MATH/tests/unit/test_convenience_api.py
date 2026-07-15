"""
Tests for Convenience API
"""

import numpy as np
import geo_infer_math.api as math_api
from geo_infer_math.api.convenience import (
    ActiveInferenceConvenience,
    BayesianConvenience,
    AIConvenience,
)
from geo_infer_math.utils.conversion import format_coordinate_string


def test_api_package_imports_without_web_stack():
    """Convenience API imports should not require Flask-backed web APIs."""
    assert "ActiveInferenceConvenience" in math_api.__all__
    assert hasattr(math_api, "ActiveInferenceConvenience")


def test_act_convenience():
    """Test Active Inference convenience."""
    conv = ActiveInferenceConvenience()
    observations = np.random.rand(10)
    beliefs = np.ones(5) / 5

    free_energy = conv.calculate_free_energy(observations, beliefs)
    assert np.isfinite(free_energy)


def test_bayes_convenience():
    """Test Bayesian convenience."""
    conv = BayesianConvenience()
    prior = conv.build_prior("uniform", size=10)
    assert len(prior) == 10
    assert np.isclose(np.sum(prior), 1.0)


def test_ai_convenience():
    """Test AI convenience."""
    conv = AIConvenience()

    def objective(x):
        return np.sum(x**2)

    initial = np.array([1.0, 2.0])
    gradient = conv.compute_gradient(objective, initial)
    assert len(gradient) == len(initial)


def test_format_coordinate_string_preserves_coordinate_values():
    """Coordinate formatting should render values, not format templates."""
    assert format_coordinate_string(40.7128, -74.006, "decimal") == (
        "40.712800, -74.006000"
    )
    assert format_coordinate_string(40.5, -74.0, "dms") == (
        "40°30'00.0\"N, 74°00'00.0\"W"
    )
    assert format_coordinate_string(40.5, -74.0, "dm") == "40°30.00'N, 74°00.00'W"
