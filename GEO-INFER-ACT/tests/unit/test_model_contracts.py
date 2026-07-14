"""Property-based contracts for finite, normalized, reproducible ACT models."""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import given, strategies as st

from geo_infer_act.models.base import CategoricalModel
from geo_infer_act.models.resource import ResourceModel
from geo_infer_test.testing import (
    assert_probability,
    assert_same_finite_values,
    assert_stochastic_matrix,
)


@given(
    state_dim=st.integers(min_value=1, max_value=8),
    obs_dim=st.integers(min_value=1, max_value=8),
)
def test_categorical_posteriors_are_normalized_for_any_valid_dimensions(
    state_dim: int, obs_dim: int
) -> None:
    """Valid categorical dimensions always yield finite normalized posteriors."""
    model = CategoricalModel(state_dim=state_dim, obs_dim=obs_dim)
    observation = np.arange(1, obs_dim + 1, dtype=float)
    posterior = model.update_beliefs(observation)
    assert posterior.shape == (state_dim,)
    assert_probability(posterior, name="categorical.posterior")


@given(
    dimension=st.integers(min_value=1, max_value=6),
    values=st.lists(
        st.floats(
            min_value=0.01, max_value=10.0, allow_nan=False, allow_infinity=False
        ),
        min_size=36,
        max_size=36,
    ),
)
def test_stochastic_matrix_contract_normalizes_nonnegative_rows(
    dimension: int, values: list[float]
) -> None:
    """Every valid nonnegative transition matrix is row-stochastic after setting."""
    matrix = np.asarray(values[: dimension * dimension], dtype=float).reshape(
        dimension, dimension
    )
    model = CategoricalModel(state_dim=dimension, obs_dim=dimension)
    model.set_transition_matrix(matrix)
    assert_stochastic_matrix(model.transition_matrix, axis=1, name="transition")


@given(seed=st.integers(min_value=0, max_value=10000))
def test_resource_model_seed_replay_and_reset_are_exact(seed: int) -> None:
    """A resource model replays exactly and restores its seeded initial state."""
    first = ResourceModel(n_resources=2, n_locations=3, random_seed=seed)
    second = ResourceModel(n_resources=2, n_locations=3, random_seed=seed)
    first_state, _ = first.step()
    second_state, _ = second.step()
    assert_same_finite_values(
        first_state["resource_distribution"],
        second_state["resource_distribution"],
        name="resource.seed_replay",
    )
    first.reset()
    assert_same_finite_values(
        first.resource_distribution,
        first._initial_resource_distribution,
        name="resource.reset",
    )


def test_model_contract_rejects_invalid_shapes_and_nonfinite_observations() -> None:
    """Invalid model inputs fail explicitly instead of producing silent fallback output."""
    model = CategoricalModel(state_dim=2, obs_dim=2)
    with pytest.raises(ValueError, match="Observation"):
        model.update_beliefs(np.array([1.0]))
    with pytest.raises(ValueError, match="finite"):
        model.update_beliefs(np.array([np.nan, 1.0]))
