"""Regression tests for numerical and inference-contract hardening."""

import numpy as np
import pytest

from geo_infer_act.core.belief_updating import BayesianBeliefUpdate
from geo_infer_act.core.dynamic_causal_model import DynamicCausalModel
from geo_infer_act.core.policy_selection import PolicySelector
from geo_infer_act.core.variational_inference import VariationalInference
from geo_infer_act.models.multi_agent import MultiAgentModel
from geo_infer_act.utils.math import (
    compute_surprise,
    sample_categorical,
    softmax,
)


def test_softmax_rejects_invalid_temperature_and_nonfinite_values() -> None:
    with pytest.raises(ValueError, match="strictly positive"):
        softmax(np.array([1.0, 2.0]), temperature=0.0)
    with pytest.raises(ValueError, match="finite"):
        softmax(np.array([1.0, np.nan]))


def test_categorical_sampling_does_not_mutate_global_rng() -> None:
    np.random.seed(123)
    before = np.random.random()
    sample_categorical(np.array([0.2, 0.8]), n_samples=3, random_state=7)
    after = np.random.random()

    np.random.seed(123)
    np.testing.assert_allclose([before, after], np.random.random(2))


def test_continuous_surprise_is_scalar_and_sigma_is_validated() -> None:
    result = compute_surprise(np.array([0.4, 0.6]), np.array([0.5, 0.5]))
    assert isinstance(result, float)
    assert np.isfinite(result)
    with pytest.raises(ValueError, match="strictly positive"):
        compute_surprise(np.array([0.4, 0.6]), np.array([0.5, 0.5]), sigma=0.0)


def test_gaussian_update_preserves_symmetric_positive_definite_precision() -> None:
    updater = BayesianBeliefUpdate()
    result = updater.update_gaussian(
        np.zeros(2),
        np.eye(2),
        np.array([1.0, -1.0]),
        np.eye(2),
        np.eye(2) * 10.0,
    )
    precision = result["precision"]
    np.testing.assert_allclose(precision, precision.T)
    assert np.all(np.linalg.eigvalsh(precision) > 0)


def test_policy_expected_posterior_uses_information_gain() -> None:
    selector = PolicySelector(selection_mode="deterministic")
    breakdown = selector.compute_expected_free_energy(
        np.array([0.5, 0.5]),
        {
            "predicted_beliefs": np.array([0.5, 0.5]),
            "expected_posterior": np.array([1.0, 0.0]),
            "exploration_bonus": 1.0,
        },
        return_breakdown=True,
    )
    assert breakdown.epistemic_value == pytest.approx(np.log(2.0))
    assert breakdown.metadata["epistemic_value_source"] == "expected_posterior_kl"


def test_policy_rejects_nonpositive_temperature() -> None:
    with pytest.raises(ValueError, match="strictly positive"):
        PolicySelector(temperature=-1.0)


def test_factor_graph_message_passing_uses_pairwise_potential() -> None:
    vi = VariationalInference(max_iterations=30)
    result = vi.structured_update(
        {
            "variables": {"x": {"dimension": 2}, "y": {"dimension": 2}},
            "factors": {
                "agreement": {
                    "variables": ["x", "y"],
                    "potential": np.array([[4.0, 1.0], [1.0, 4.0]]),
                }
            },
        },
        {"y": np.array([1.0, 0.0])},
    )
    np.testing.assert_array_equal(result["y"], [1.0, 0.0])
    assert result["x"][0] > result["x"][1]
    np.testing.assert_allclose(result["x"].sum(), 1.0)


def test_dynamic_causal_model_rejects_nonmonotonic_time() -> None:
    model = DynamicCausalModel(2, 1, 1)
    with pytest.raises(ValueError, match="strictly increasing"):
        model.integrate_dynamics(
            np.zeros(2), np.zeros((2, 1)), np.array([0.0, 0.0])
        )


def test_multi_agent_step_updates_beliefs_and_harvests_requested_resource() -> None:
    model = MultiAgentModel(
        n_agents=1,
        n_resources=1,
        n_locations=2,
        random_seed=3,
    )
    before = model.resource_distribution[0, 1]
    state, done = model.step(
        [
            {
                "agent_id": 0,
                "location": 1,
                "resource": 0,
                "amount": 0.1,
                "observation": np.array([1.0, 0.0, 0.0, 0.0]),
            }
        ]
    )
    assert done is False
    assert state["step"] == 1
    assert state["agent_locations"] == [1]
    assert state["beliefs"][0][0] > 0
    assert state["resource_distribution"][0, 1] < before
    assert state["harvest_yield"][0, 1] == pytest.approx(0.1)
