"""
Unit tests for the Policy Selection module.

Tests the PolicySelector class which implements policy selection based on
expected free energy minimization, balancing exploration (epistemic value)
and exploitation (pragmatic value) in the active inference framework.
"""

import numpy as np
import pytest

from geo_infer_act.core.policy_selection import PolicySelector


class TestPolicySelectorInit:
    """Test PolicySelector initialization."""

    def test_default_temperature(self) -> None:
        """Test default temperature parameter."""
        selector = PolicySelector()
        assert selector.temperature == 1.0

    def test_custom_temperature(self) -> None:
        """Test custom temperature parameter."""
        selector = PolicySelector(temperature=0.5)
        assert selector.temperature == 0.5


class TestPolicySelection:
    """Test policy selection mechanics."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.selector = PolicySelector(temperature=1.0)

    def test_select_from_explicit_policies(self) -> None:
        """Test selecting from an explicit list of policies."""
        beliefs = np.array([0.4, 0.3, 0.2, 0.1])
        policies = [
            {'action': 0, 'exploration_bonus': 0.1},
            {'action': 1, 'exploration_bonus': 0.2},
            {'action': 2, 'exploration_bonus': 0.3},
        ]
        preferences = np.array([0.1, 0.2, 0.3, 0.4])

        result = self.selector.select_policy(beliefs, policies, preferences)
        assert 'policy' in result
        assert 'probability' in result
        assert 'expected_free_energy' in result
        assert 'all_probabilities' in result
        assert 'all_free_energies' in result
        assert result['policy'] in policies
        assert 0.0 <= result['probability'] <= 1.0

    def test_probabilities_sum_to_one(self) -> None:
        """Test that all policy probabilities sum to 1."""
        beliefs = np.array([0.5, 0.3, 0.2])
        policies = [
            {'action': i, 'exploration_bonus': 0.1 * i}
            for i in range(5)
        ]
        result = self.selector.select_policy(beliefs, policies)
        np.testing.assert_allclose(
            result['all_probabilities'].sum(), 1.0, atol=1e-6
        )

    def test_default_policies_when_empty(self) -> None:
        """Test that default policies are created when none provided."""
        beliefs = np.array([0.5, 0.3, 0.2])
        result = self.selector.select_policy(beliefs, [])
        assert 'policy' in result
        assert len(result['all_probabilities']) == 5  # Default creates 5 policies


class TestExpectedFreeEnergyComputation:
    """Test expected free energy computation for policies."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.selector = PolicySelector()

    def test_efe_returns_float(self) -> None:
        """Test that EFE computation returns a float."""
        beliefs = np.array([0.25, 0.25, 0.25, 0.25])
        policy = {'exploration_bonus': 0.1, 'risk_preference': 0.0}
        efe = self.selector.compute_expected_free_energy(beliefs, policy)
        assert isinstance(efe, float)
        assert np.isfinite(efe)

    def test_efe_with_preferences(self) -> None:
        """Test EFE with explicit preferences."""
        beliefs = np.array([0.5, 0.3, 0.2])
        policy = {'exploration_bonus': 0.1, 'temporal_discount': 0.9}
        preferences = np.array([0.1, 0.3, 0.6])
        efe = self.selector.compute_expected_free_energy(beliefs, policy, preferences)
        assert np.isfinite(efe)

    def test_integer_policy_conversion(self) -> None:
        """Test that integer policies are handled gracefully."""
        beliefs = np.array([0.5, 0.5])
        efe = self.selector.compute_expected_free_energy(beliefs, 0)
        assert np.isfinite(efe)

    def test_risk_averse_vs_seeking(self) -> None:
        """Test that risk preference modulates expected free energy."""
        beliefs = np.array([0.6, 0.2, 0.1, 0.1])
        risk_averse = {'exploration_bonus': 0.1, 'risk_preference': -0.5}
        risk_seeking = {'exploration_bonus': 0.1, 'risk_preference': 0.5}

        efe_averse = self.selector.compute_expected_free_energy(beliefs, risk_averse)
        efe_seeking = self.selector.compute_expected_free_energy(beliefs, risk_seeking)
        assert efe_averse != efe_seeking


class TestPolicyPrecision:
    """Test policy precision computation."""

    def test_differentiated_policies_higher_precision(self) -> None:
        """Test that well-differentiated policies produce higher precision."""
        selector = PolicySelector()
        well_diff = np.array([0.1, 0.5, 1.0, 2.0, 3.0])
        poorly_diff = np.array([1.0, 1.01, 1.02, 1.03, 1.04])

        prec_well = selector.compute_policy_precision(well_diff)
        prec_poor = selector.compute_policy_precision(poorly_diff)
        assert prec_well > prec_poor


class TestPolicySetEvaluation:
    """Test evaluation of complete policy sets."""

    def test_evaluate_returns_complete_info(self) -> None:
        """Test that evaluation returns all expected fields."""
        selector = PolicySelector()
        beliefs = np.array([0.4, 0.3, 0.2, 0.1])
        policies = [
            {'action': i, 'exploration_bonus': 0.1}
            for i in range(3)
        ]
        result = selector.evaluate_policy_set(beliefs, policies)
        assert 'policies' in result
        assert 'expected_free_energies' in result
        assert 'epistemic_values' in result
        assert 'pragmatic_values' in result
        assert 'probabilities' in result
        assert 'best_policy_idx' in result
        assert 'diversity' in result

    def test_best_policy_index_valid(self) -> None:
        """Test that best policy index is within valid range."""
        selector = PolicySelector()
        beliefs = np.array([0.5, 0.3, 0.2])
        policies = [
            {'action': i, 'exploration_bonus': 0.1 * (i + 1)}
            for i in range(4)
        ]
        result = selector.evaluate_policy_set(beliefs, policies)
        assert 0 <= result['best_policy_idx'] < 4


class TestActionSelection:
    """Test single action selection."""

    def test_select_action_from_list(self) -> None:
        """Test selecting a single action from available actions."""
        selector = PolicySelector()
        beliefs = np.array([0.5, 0.3, 0.2])
        actions = [0, 1, 2]
        action = selector.select_action(beliefs, actions)
        assert action in actions

    def test_single_action_returns_it(self) -> None:
        """Test that a single available action is always returned."""
        selector = PolicySelector()
        beliefs = np.array([0.5, 0.5])
        action = selector.select_action(beliefs, [42])
        assert action == 42

    def test_empty_actions_returns_none(self) -> None:
        """Test that empty action list returns None."""
        selector = PolicySelector()
        beliefs = np.array([0.5, 0.5])
        action = selector.select_action(beliefs, [])
        assert action is None
