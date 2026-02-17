"""
Unit tests for the Climate Active Inference Model.

Tests the ClimateModel class which implements climate adaptation modeling
using Active Inference with temperature and CO2 state factors.
"""

import numpy as np
import pytest

from geo_infer_act.models.climate import ClimateModel
from geo_infer_act.core.active_inference import ActiveInferenceModel


class TestClimateModelInit:
    """Test ClimateModel initialization."""

    def test_default_initialization(self) -> None:
        """Test that ClimateModel initializes with correct dimensions."""
        model = ClimateModel()
        assert model.num_states == [3, 3]
        assert model.num_obs == [3, 3]
        assert model.num_controls == [3, 3]
        assert model.state_factors == ["Temperature", "CO2"]
        assert model.obs_factors == ["Thermometer", "CO2Sensor"]

    def test_inherits_active_inference(self) -> None:
        """Test that ClimateModel is a valid ActiveInferenceModel."""
        model = ClimateModel()
        assert isinstance(model, ActiveInferenceModel)

    def test_generative_model_set(self) -> None:
        """Test that the generative model is properly configured."""
        model = ClimateModel()
        assert model.generative_model is not None
        assert model.generative_model.observation_model is not None
        assert model.generative_model.transition_model is not None
        assert model.generative_model.preferences is not None


class TestClimateModelMatrices:
    """Test the climate model's generative model matrices."""

    def test_likelihood_a_structure(self) -> None:
        """Test A matrix (likelihood) has correct shape and normalization."""
        model = ClimateModel()
        A = model._build_likelihood_A()
        assert len(A) == 2
        # Thermometer: (3 obs) x (3 temp states) x (3 CO2 states)
        assert A[0].shape == (3, 3, 3)
        # CO2 sensor: (3 obs) x (3 temp states) x (3 CO2 states)
        assert A[1].shape == (3, 3, 3)
        # For each state combination, observations should sum to ~1
        for i_temp in range(3):
            for i_co2 in range(3):
                np.testing.assert_allclose(
                    A[0][:, i_temp, i_co2].sum(), 1.0, atol=1e-6
                )
                np.testing.assert_allclose(
                    A[1][:, i_temp, i_co2].sum(), 1.0, atol=1e-6
                )

    def test_transition_b_normalization(self) -> None:
        """Test B matrix columns sum to 1 for each state-action pair."""
        model = ClimateModel()
        B = model._build_transition_B()
        assert len(B) == 2
        # Temperature transitions: (3, 3, 3) = (next, current, action)
        assert B[0].shape == (3, 3, 3)
        for action in range(3):
            for state in range(3):
                col_sum = B[0][:, state, action].sum()
                np.testing.assert_allclose(col_sum, 1.0, atol=1e-6)

    def test_preferences_encode_climate_goals(self) -> None:
        """Test C matrix encodes preference for normal temperature and safe CO2."""
        model = ClimateModel()
        C = model._build_preferences_C()
        # Prefer Normal Temperature (index 0 has highest value)
        assert C[0][0] > C[0][1] > C[0][2]
        # Prefer Safe CO2 (index 0 has highest value)
        assert C[1][0] > C[1][1] > C[1][2]

    def test_prior_d_initial_state(self) -> None:
        """Test D matrix starts at normal/safe conditions."""
        model = ClimateModel()
        D = model._build_prior_D()
        assert len(D) == 2
        # Highest prior probability on Normal temperature
        assert D[0][0] > D[0][1]
        assert D[0][0] > D[0][2]
        # Highest prior probability on Safe CO2
        assert D[1][0] > D[1][1]
        assert D[1][0] > D[1][2]


class TestClimateModelStep:
    """Test climate model step execution."""

    def test_step_with_observations(self) -> None:
        """Test step with explicit observations."""
        model = ClimateModel()
        result = model.step([0, 0])  # Normal temp, safe CO2 observations
        assert isinstance(result, tuple)
        beliefs, action = result
        assert beliefs is not None

    def test_step_default_observation(self) -> None:
        """Test step with default (None) observation."""
        model = ClimateModel()
        result = model.step()
        assert isinstance(result, tuple)

    def test_climate_crisis_observation_shifts_beliefs(self) -> None:
        """Test that crisis observations shift beliefs appropriately."""
        model = ClimateModel()
        # Observe high temperature and critical CO2
        result = model.step([2, 2])
        assert isinstance(result, tuple)

    def test_config_override(self) -> None:
        """Test that custom config can be provided."""
        config = {'exploration_bonus': 0.5}
        model = ClimateModel(config=config)
        assert model is not None
