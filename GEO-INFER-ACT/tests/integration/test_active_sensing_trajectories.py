"""
Integration tests for active sensing trajectories and policy convergence in
ACT's active-inference stacks.

These surface emergent behaviour across successive updates:

- a continuous Laplace filter sharpens (variance shrinks) under consistent
  observations — active sensing resolves uncertainty;
- a single-cell spatial agent's information-gain score drops as its belief
  becomes confident — the "where to look next" signal collapses to zero;
- the composed policy posterior sharpens as its precision grows — converging
  onto a single preferred policy.
"""

from __future__ import annotations

import numpy as np
import pytest

from geo_infer_act.core.policy_selection import PolicySelector
from geo_infer_act.core.spatial_agent import SpatialActiveInferenceAgent
from geo_infer_act.models.continuous_pomdp import ContinuousPOMDPActiveInference
from geo_infer_act.utils.h3_adapter import get_h3_adapter


def _one_cell() -> str:
    adapter = get_h3_adapter()
    return adapter.latlng_to_cell(37.7749, -122.4194, 9)


def test_laplace_filter_sharpens_belief_under_consistent_sensing() -> None:
    """Repeated consistent observations monotonically reduce belief spread."""
    model = ContinuousPOMDPActiveInference(
        state_dim=2, obs_dim=2, action_dim=2, dt=0.1
    )
    observation = np.array([1.0, 1.0])
    traces = []
    for _ in range(15):
        _, sigma, _ = model.update_beliefs(observation)
        traces.append(float(np.trace(sigma)))
    # Belief covariance is strictly monotonically non-increasing.
    assert all(trace_after <= trace_before for trace_before, trace_after in zip(traces, traces[1:]))
    assert traces[-1] < traces[0]


def test_active_sensing_information_gain_collapses_when_resolved() -> None:
    """A confident single-cell agent no longer suggests it should look closer."""
    agent = SpatialActiveInferenceAgent(initial_cells=[_one_cell()], state_dim=4)
    observation = {_one_cell(): np.array([1.0, 0.0, 0.0, 0.0])}
    # Uniform initial belief → score starts at ~1.0.
    initial_score = agent.score_spatial_information_gain()["scores"][_one_cell()]
    for _ in range(12):
        agent.step(observation)
    final_score = agent.score_spatial_information_gain()["scores"][_one_cell()]
    assert initial_score > 0.99
    assert final_score < 0.5
    assert final_score < initial_score


def test_policy_posterior_converges_with_precision() -> None:
    """Higher adaptive precision concentrates the policy posterior."""
    selector = PolicySelector()
    scores = np.array([0.0, 5.0, -3.0])
    probes = [1.0, 2.0, 5.0, 20.0, 100.0]
    best_values = []
    for precision in probes:
        assembled = selector.compose_policy_posterior(scores, precision=precision)
        best = float(np.max(np.asarray(assembled["posterior"], dtype=float)))
        best_values.append(best)
    # Sharper precision → the argmin policy's probability grows toward 1.
    assert best_values[-1] > best_values[0]
    assert best_values[-1] > 0.9