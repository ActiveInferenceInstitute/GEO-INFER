"""
Unit tests for the Markov Decision Process module.

Tests the MarkovDecisionProcess class which implements discrete
state-space dynamics and observation models for active inference,
including transition sampling, observation generation, and
belief updating via Bayes' rule.
"""

import numpy as np
import pytest

from geo_infer_act.core.markov_decision_process import MarkovDecisionProcess


class TestMDPInitialization:
    """Test MDP initialization and validation."""

    def test_default_initialization(self) -> None:
        """Test MDP initializes with uniform distributions by default."""
        mdp = MarkovDecisionProcess(n_states=3, n_observations=2, n_actions=2)
        assert mdp.n_states == 3
        assert mdp.n_observations == 2
        assert mdp.n_actions == 2
        assert mdp.transition_prob.shape == (3, 3, 2)
        assert mdp.observation_prob.shape == (2, 3)

    def test_custom_transition_matrix(self) -> None:
        """Test initialization with custom transition probabilities."""
        trans = np.zeros((2, 2, 2))
        # Action 0: stay in same state
        trans[0, :, 0] = [1.0, 0.0]
        trans[1, :, 0] = [0.0, 1.0]
        # Action 1: switch states
        trans[0, :, 1] = [0.0, 1.0]
        trans[1, :, 1] = [1.0, 0.0]

        obs = np.array([[0.9, 0.1], [0.1, 0.9]])

        mdp = MarkovDecisionProcess(
            n_states=2,
            n_observations=2,
            n_actions=2,
            transition_prob=trans,
            observation_prob=obs,
        )
        np.testing.assert_array_equal(mdp.transition_prob, trans)

    def test_invalid_transition_shape_raises(self) -> None:
        """Test that wrong transition matrix shape raises ValueError."""
        bad_trans = np.ones((3, 3, 3)) / 3
        with pytest.raises(ValueError, match="shape"):
            MarkovDecisionProcess(
                n_states=3, n_observations=2, n_actions=2, transition_prob=bad_trans
            )

    def test_invalid_observation_shape_raises(self) -> None:
        """Test that wrong observation matrix shape raises ValueError."""
        bad_obs = np.ones((3, 3)) / 3
        with pytest.raises(ValueError, match="shape"):
            MarkovDecisionProcess(
                n_states=3, n_observations=2, n_actions=2, observation_prob=bad_obs
            )

    def test_non_normalized_transition_raises(self) -> None:
        """Test that non-normalized transition probabilities raise ValueError."""
        trans = np.ones((3, 3, 2))  # Sums to 3, not 1
        with pytest.raises(ValueError, match="sum to"):
            MarkovDecisionProcess(
                n_states=3, n_observations=2, n_actions=2, transition_prob=trans
            )

    def test_non_positive_dimensions_raise(self) -> None:
        """The state, observation, and action spaces must be non-empty."""
        with pytest.raises(ValueError, match="positive integer"):
            MarkovDecisionProcess(n_states=0, n_observations=2, n_actions=1)


class TestMDPTransitions:
    """Test MDP state transitions."""

    def setup_method(self) -> None:
        """Set up a deterministic MDP for testing."""
        np.random.seed(42)
        trans = np.zeros((3, 3, 2))
        # Action 0: clockwise rotation (0->1->2->0)
        trans[0, 1, 0] = 1.0
        trans[1, 2, 0] = 1.0
        trans[2, 0, 0] = 1.0
        # Action 1: stay
        trans[0, 0, 1] = 1.0
        trans[1, 1, 1] = 1.0
        trans[2, 2, 1] = 1.0

        obs = np.eye(3)  # Perfect observation

        self.mdp = MarkovDecisionProcess(
            n_states=3,
            n_observations=3,
            n_actions=2,
            transition_prob=trans,
            observation_prob=obs,
        )

    def test_deterministic_transition(self) -> None:
        """Test deterministic state transitions."""
        next_state = self.mdp.transition(0, 0)
        assert next_state == 1  # 0 -> 1 under action 0

    def test_stay_action(self) -> None:
        """Test that stay action keeps state unchanged."""
        for state in range(3):
            next_state = self.mdp.transition(state, 1)
            assert next_state == state

    def test_get_transition_prob(self) -> None:
        """Test transition probability retrieval."""
        probs = self.mdp.get_transition_prob(0, 0)
        expected = np.array([0.0, 1.0, 0.0])
        np.testing.assert_array_equal(probs, expected)


class TestMDPObservations:
    """Test MDP observation generation."""

    def test_deterministic_observation(self) -> None:
        """Test observation with identity observation matrix."""
        obs_prob = np.eye(3)
        mdp = MarkovDecisionProcess(
            n_states=3, n_observations=3, n_actions=1, observation_prob=obs_prob
        )
        obs = mdp.observe(1)
        assert obs == 1

    def test_get_observation_prob(self) -> None:
        """Test observation probability retrieval."""
        obs_prob = np.array([[0.8, 0.2], [0.2, 0.8]])
        mdp = MarkovDecisionProcess(
            n_states=2, n_observations=2, n_actions=1, observation_prob=obs_prob
        )
        probs = mdp.get_observation_prob(0)
        np.testing.assert_array_equal(probs, np.array([0.8, 0.2]))


class TestMDPSimulation:
    """Test MDP trajectory simulation."""

    def test_simulation_trajectory_lengths(self) -> None:
        """Test that simulation produces correct trajectory lengths."""
        mdp = MarkovDecisionProcess(n_states=4, n_observations=3, n_actions=2)
        policy = [0, 1, 0, 1, 0]
        states, obs = mdp.simulate(initial_state=0, policy=policy)
        # Should have initial + len(policy) states
        assert len(states) == 6
        assert len(obs) == 6

    def test_deterministic_simulation(self) -> None:
        """Test deterministic simulation mode."""
        trans = np.zeros((2, 2, 1))
        trans[0, 1, 0] = 1.0  # State 0 always goes to state 1
        trans[1, 0, 0] = 1.0  # State 1 always goes to state 0
        obs_prob = np.eye(2)

        mdp = MarkovDecisionProcess(
            n_states=2,
            n_observations=2,
            n_actions=1,
            transition_prob=trans,
            observation_prob=obs_prob,
        )
        states, obs = mdp.simulate(0, [0, 0, 0, 0], stochastic=False)
        assert states == [0, 1, 0, 1, 0]

    def test_stochastic_simulation_varies(self) -> None:
        """Test that stochastic simulation can produce different outcomes."""
        mdp = MarkovDecisionProcess(n_states=4, n_observations=4, n_actions=2)
        trajectories = set()
        for seed in range(10):
            np.random.seed(seed)
            states, _ = mdp.simulate(0, [0, 1, 0])
            trajectories.add(tuple(states))
        # With uniform transitions, we should get at least some variation
        assert len(trajectories) > 1


class TestMDPBeliefUpdating:
    """Test MDP belief updating via Bayes' rule."""

    def test_belief_update_normalizes(self) -> None:
        """Test that belief update produces normalized distribution."""
        obs_prob = np.array([[0.8, 0.2], [0.2, 0.8]])
        mdp = MarkovDecisionProcess(
            n_states=2, n_observations=2, n_actions=1, observation_prob=obs_prob
        )
        prior = np.array([0.5, 0.5])
        posterior = mdp.update_belief(prior, observation=0)
        np.testing.assert_allclose(posterior.sum(), 1.0, atol=1e-10)

    def test_observation_shifts_belief(self) -> None:
        """Test that observations shift beliefs toward the correct state."""
        obs_prob = np.array([[0.9, 0.1], [0.1, 0.9]])
        mdp = MarkovDecisionProcess(
            n_states=2, n_observations=2, n_actions=1, observation_prob=obs_prob
        )
        prior = np.array([0.5, 0.5])
        posterior = mdp.update_belief(prior, observation=0)
        # Observation 0 is more likely from state 0
        assert posterior[0] > posterior[1]

    def test_zero_support_observation_raises(self) -> None:
        """Impossible observations must not return NaN beliefs."""
        obs_prob = np.array([[1.0, 0.0], [0.0, 1.0]])
        mdp = MarkovDecisionProcess(
            n_states=2, n_observations=2, n_actions=1, observation_prob=obs_prob
        )
        with pytest.raises(ValueError, match="zero posterior support"):
            mdp.update_belief(np.array([0.0, 1.0]), observation=0)

    def test_predictive_state(self) -> None:
        """Test predictive state distribution after action."""
        mdp = MarkovDecisionProcess(n_states=3, n_observations=2, n_actions=2)
        belief = np.array([0.5, 0.3, 0.2])
        pred = mdp.get_predictive_state(belief, action=0)
        np.testing.assert_allclose(pred.sum(), 1.0, atol=1e-10)

    def test_predictive_observation(self) -> None:
        """Test predictive observation distribution."""
        mdp = MarkovDecisionProcess(n_states=3, n_observations=2, n_actions=1)
        state_dist = np.array([0.5, 0.3, 0.2])
        pred_obs = mdp.get_predictive_observation(state_dist)
        np.testing.assert_allclose(pred_obs.sum(), 1.0, atol=1e-10)
        assert pred_obs.shape == (2,)


class TestMDPMatrixSetting:
    """Test setting transition and observation matrices."""

    def test_set_transition_matrix(self) -> None:
        """Test setting transition distribution for specific state-action pair."""
        mdp = MarkovDecisionProcess(n_states=3, n_observations=2, n_actions=2)
        new_dist = np.array([0.1, 0.2, 0.7])
        mdp.set_transition_matrix(state=0, action=1, distribution=new_dist)
        np.testing.assert_array_equal(mdp.transition_prob[0, :, 1], new_dist)

    def test_set_transition_invalid_shape_raises(self) -> None:
        """Test that wrong shape raises ValueError."""
        mdp = MarkovDecisionProcess(n_states=3, n_observations=2, n_actions=2)
        with pytest.raises(ValueError, match="shape"):
            mdp.set_transition_matrix(0, 0, np.array([0.5, 0.5]))

    def test_set_transition_non_normalized_raises(self) -> None:
        """Test that non-normalized distribution raises ValueError."""
        mdp = MarkovDecisionProcess(n_states=3, n_observations=2, n_actions=2)
        with pytest.raises(ValueError, match="sum to 1"):
            mdp.set_transition_matrix(0, 0, np.array([0.5, 0.5, 0.5]))

    def test_set_observation_matrix(self) -> None:
        """Test setting observation distribution for a specific state."""
        mdp = MarkovDecisionProcess(n_states=2, n_observations=3, n_actions=1)
        new_dist = np.array([0.2, 0.3, 0.5])
        mdp.set_observation_matrix(state=0, distribution=new_dist)
        np.testing.assert_array_equal(mdp.observation_prob[:, 0], new_dist)
