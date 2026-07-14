"""
Unit tests for the Dynamic Causal Model.

Tests the DynamicCausalModel class which implements continuous-time
active inference using stochastic differential equations and
Kalman filtering for state estimation.
"""

import numpy as np
import pytest

from geo_infer_act.core.dynamic_causal_model import DynamicCausalModel


class TestDCMInitialization:
    """Test DCM initialization and parameter setup."""

    def test_default_initialization(self) -> None:
        """Test that DCM initializes with correct dimensions."""
        dcm = DynamicCausalModel(state_dim=3, input_dim=2, output_dim=2)
        assert dcm.state_dim == 3
        assert dcm.input_dim == 2
        assert dcm.output_dim == 2
        assert dcm.dt == 0.01

    def test_matrix_dimensions(self) -> None:
        """Test that internal matrices have correct shapes."""
        dcm = DynamicCausalModel(state_dim=4, input_dim=2, output_dim=3)
        assert dcm.A.shape == (4, 4)
        assert dcm.B.shape == (4, 2)
        assert dcm.C.shape == (3, 4)
        assert dcm.Q.shape == (4, 4)
        assert dcm.R.shape == (3, 3)

    def test_initial_state_is_zero(self) -> None:
        """Test that initial state vector is zero."""
        dcm = DynamicCausalModel(state_dim=5, input_dim=1, output_dim=1)
        np.testing.assert_array_equal(dcm.state, np.zeros(5))

    def test_custom_dt(self) -> None:
        """Test custom time step."""
        dcm = DynamicCausalModel(state_dim=2, input_dim=1, output_dim=1, dt=0.05)
        assert dcm.dt == 0.05


class TestDCMDynamics:
    """Test DCM state evolution and observation equations."""

    def setup_method(self) -> None:
        """Set up a simple deterministic DCM for testing."""
        np.random.seed(42)
        self.dcm = DynamicCausalModel(state_dim=2, input_dim=1, output_dim=2)
        # Set known parameters for deterministic testing
        self.dcm.A = np.array([[-0.5, 0.0], [0.0, -0.3]])
        self.dcm.B = np.array([[1.0], [0.5]])
        self.dcm.C = np.eye(2)
        self.dcm.Q = np.eye(2) * 0.001
        self.dcm.R = np.eye(2) * 0.001

    def test_state_equation_linear(self) -> None:
        """Test state equation computes dx/dt = Ax + Bu."""
        state = np.array([1.0, 2.0])
        inputs = np.array([0.5])
        dxdt = self.dcm.state_equation(state, 0.0, inputs)
        expected = self.dcm.A @ state + self.dcm.B @ inputs
        np.testing.assert_allclose(dxdt, expected)

    def test_observation_equation_output(self) -> None:
        """Test observation equation produces output of correct dimension."""
        state = np.array([1.0, -0.5])
        obs = self.dcm.observation_equation(state)
        assert obs.shape == (2,)

    def test_integrate_dynamics_trajectory_shape(self) -> None:
        """Test that dynamics integration produces correct trajectory shape."""
        initial_state = np.array([1.0, 0.0])
        time_points = np.linspace(0, 1.0, 50)
        inputs = np.zeros((50, 1))
        trajectory = self.dcm.integrate_dynamics(initial_state, inputs, time_points)
        assert trajectory.shape == (50, 2)
        # First point should be the initial state
        np.testing.assert_array_equal(trajectory[0], initial_state)

    def test_stable_dynamics_decay(self) -> None:
        """Test that with negative eigenvalues, states decay toward zero."""
        initial_state = np.array([5.0, 3.0])
        time_points = np.linspace(0, 10.0, 200)
        inputs = np.zeros((200, 1))
        # Use very low noise for this test
        self.dcm.Q = np.eye(2) * 1e-10
        trajectory = self.dcm.integrate_dynamics(initial_state, inputs, time_points)
        # Final state should be closer to zero than initial
        assert np.linalg.norm(trajectory[-1]) < np.linalg.norm(initial_state)


class TestDCMObservations:
    """Test observation generation from state trajectories."""

    def test_generate_observations_shape(self) -> None:
        """Test observation generation produces correct shape."""
        dcm = DynamicCausalModel(state_dim=3, input_dim=1, output_dim=2)
        trajectory = np.random.randn(20, 3)
        observations = dcm.generate_observations(trajectory)
        assert observations.shape == (20, 2)

    def test_observation_noise_nonzero(self) -> None:
        """Test that observations include noise (not exactly C*x)."""
        np.random.seed(42)
        dcm = DynamicCausalModel(state_dim=2, input_dim=1, output_dim=2)
        dcm.C = np.eye(2)
        dcm.R = np.eye(2) * 0.1
        state = np.array([1.0, 2.0])
        obs = dcm.observation_equation(state)
        deterministic = dcm.C @ state
        # With noise, observations should differ from deterministic output
        assert not np.allclose(obs, deterministic, atol=1e-10)


class TestDCMParameterEstimation:
    """Test DCM parameter estimation from data."""

    def setup_method(self) -> None:
        """Create a DCM with known parameters and generate data."""
        np.random.seed(42)
        self.dcm = DynamicCausalModel(state_dim=2, input_dim=1, output_dim=2)
        self.dcm.A = np.array([[-0.5, 0.1], [0.1, -0.3]])
        self.dcm.B = np.array([[1.0], [0.0]])
        self.dcm.C = np.eye(2)
        self.dcm.Q = np.eye(2) * 0.001
        self.dcm.R = np.eye(2) * 0.01

        self.time_points = np.linspace(0, 5.0, 100)
        self.inputs = np.sin(self.time_points).reshape(-1, 1)
        self.initial_state = np.array([0.0, 0.0])
        self.trajectory = self.dcm.integrate_dynamics(
            self.initial_state, self.inputs, self.time_points
        )
        self.observations = self.dcm.generate_observations(self.trajectory)

    def test_estimate_parameters_returns_dict(self) -> None:
        """Test that parameter estimation returns expected structure."""
        result = self.dcm.estimate_parameters(
            self.observations, self.inputs, self.time_points
        )
        assert 'A' in result
        assert 'B' in result
        assert 'C' in result
        assert 'estimated_states' in result

    def test_empty_observations_raise_value_error(self) -> None:
        """Empty data should fail with a useful contract error."""
        with pytest.raises(ValueError, match="at least one timestep"):
            self.dcm.estimate_parameters(
                np.empty((0, 2)), np.empty((0, 1)), np.empty(0)
            )

    def test_estimated_matrices_shapes(self) -> None:
        """Test that estimated matrices have correct shapes."""
        result = self.dcm.estimate_parameters(
            self.observations, self.inputs, self.time_points
        )
        assert result['A'].shape == (2, 2)
        assert result['B'].shape == (2, 1)
        assert result['C'].shape == (2, 2)

    def test_set_parameters(self) -> None:
        """Test manual parameter setting."""
        dcm = DynamicCausalModel(state_dim=2, input_dim=1, output_dim=2)
        new_A = np.array([[-1.0, 0.0], [0.0, -1.0]])
        new_B = np.array([[0.5], [0.5]])
        new_C = np.array([[1.0, 0.0], [0.0, 1.0]])
        dcm.set_parameters(new_A, new_B, new_C)
        np.testing.assert_array_equal(dcm.A, new_A)
        np.testing.assert_array_equal(dcm.B, new_B)
        np.testing.assert_array_equal(dcm.C, new_C)

    def test_set_noise_parameters(self) -> None:
        """Test manual noise parameter setting."""
        dcm = DynamicCausalModel(state_dim=2, input_dim=1, output_dim=2)
        new_Q = np.eye(2) * 0.05
        new_R = np.eye(2) * 0.02
        dcm.set_noise_parameters(new_Q, new_R)
        np.testing.assert_array_equal(dcm.Q, new_Q)
        np.testing.assert_array_equal(dcm.R, new_R)
