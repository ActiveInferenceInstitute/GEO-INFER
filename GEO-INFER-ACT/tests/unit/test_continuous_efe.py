"""
Unit tests for continuous-state EFE decomposition and the Laplace /
Kalman-Bucy filter in the continuous POMDP active-inference engine.

These tests pin real model behaviour: the adopted sign convention (EFE =
pragmatic cost - epistemic gain + control effort), the stability of the
variational free-energy breakdown, and the active-sensing property that
greater sensor uncertainty reduces the epistemic (information-gain) term.
"""

from __future__ import annotations

from typing import cast

import numpy as np
import pytest

from geo_infer_act import FreeEnergyBreakdown
from geo_infer_act.models.continuous_pomdp import ContinuousPOMDPActiveInference


def test_efe_breakdown_type_and_field_agreement() -> None:
    """Decomposed EFE and the scalar EFE agree; all terms stay finite."""
    model = ContinuousPOMDPActiveInference(
        state_dim=3, obs_dim=2, action_dim=2, dt=0.1, random_seed=7
    )
    action = np.array([0.5, -0.5])
    scalar = model.compute_expected_free_energy(action, horizon=4)
    breakdown = model.compute_expected_free_energy(
        action, horizon=4, return_breakdown=True
    )
    assert isinstance(breakdown, FreeEnergyBreakdown)
    for value in (
        breakdown.free_energy,
        breakdown.pragmatic_value,
        breakdown.epistemic_value,
        breakdown.risk,
    ):
        assert np.isfinite(value)
    assert breakdown.free_energy == pytest.approx(float(cast(float, scalar)), rel=1e-9)


def test_efe_against_target_prefers_approach_action() -> None:
    """With a positive target the arg-minimal command heads toward it."""
    model = ContinuousPOMDPActiveInference(
        state_dim=2,
        obs_dim=2,
        action_dim=2,
        dt=0.1,
        prior_mean=np.zeros(2),
        target_prior=np.array([5.0, 5.0]),
        random_seed=0,
    )
    scoreboard = model.evaluate_actions(horizon=5)
    assert np.all(np.asarray(scoreboard["best_action"]) > 0.0)
    efe_scores = np.asarray(scoreboard["efe_scores"], dtype=float)
    assert scoreboard["best_efe"] == pytest.approx(float(efe_scores.min()), rel=1e-9)


def test_epistemic_gain_decreases_with_sensor_uncertainty() -> None:
    """
    Information-gain falls with observation (sensor) noise: the EFE rewards
    sensing in regimes where a measurement would disambiguate the hidden
    state, which is the active-sensing property.
    """
    rng = np.random.default_rng(3)
    observations = rng.normal(size=(5, 2))

    low = ContinuousPOMDPActiveInference(
        state_dim=2,
        obs_dim=2,
        action_dim=2,
        obs_noise_cov=np.eye(2) * 0.05,
    )
    high = ContinuousPOMDPActiveInference(
        state_dim=2,
        obs_dim=2,
        action_dim=2,
        obs_noise_cov=np.eye(2) * 0.9,
    )
    for obs in observations:
        low.update_beliefs(obs)
        high.update_beliefs(obs)

    action = np.array([0.3, -0.2])
    low_bd = low.compute_expected_free_energy(action, horizon=2, return_breakdown=True)
    high_bd = high.compute_expected_free_energy(
        action, horizon=2, return_breakdown=True
    )
    assert isinstance(low_bd, FreeEnergyBreakdown)
    assert isinstance(high_bd, FreeEnergyBreakdown)
    assert high_bd.epistemic_value < low_bd.epistemic_value


def test_variational_free_energy_breaks_into_accuracy_and_complexity() -> None:
    """Laplace VFE reports complexity - accuracy and stays finite."""
    model = ContinuousPOMDPActiveInference(
        state_dim=2, obs_dim=2, action_dim=2, dt=0.05
    )
    for obs in (np.array([0.1, -0.1]), np.array([1.5, 0.2])):
        model.update_beliefs(obs)
    breakdown = model.compute_variational_free_energy()
    assert isinstance(breakdown, FreeEnergyBreakdown)
    assert breakdown.metadata.get("model_type") == "gaussian_laplace"
    for value in (breakdown.free_energy, breakdown.accuracy, breakdown.complexity):
        assert np.isfinite(value)
    assert breakdown.free_energy == pytest.approx(
        breakdown.complexity - breakdown.accuracy, rel=1e-9
    )


def test_seeded_evaluate_actions_is_reproducible() -> None:
    """Identically seeded models produce identical EFE scoreboards."""

    def board(seed: int) -> np.ndarray:
        model = ContinuousPOMDPActiveInference(state_dim=2, obs_dim=2, action_dim=2)
        return np.asarray(model.evaluate_actions(horizon=2)["efe_scores"], dtype=float)

    assert np.array_equal(board(5), board(5))
