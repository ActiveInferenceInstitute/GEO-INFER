"""
Unit tests for Continuous POMDP Active Inference and Gaussian filter engine.
"""

from __future__ import annotations

import numpy as np
import pytest

from geo_infer_act.models.continuous_pomdp import ContinuousPOMDPActiveInference


def test_continuous_pomdp_initialization():
    model = ContinuousPOMDPActiveInference(
        state_dim=3,
        obs_dim=2,
        action_dim=2,
        dt=0.05,
        random_seed=42,
    )
    assert model.state_dim == 3
    assert model.obs_dim == 2
    assert model.action_dim == 2
    assert model.mu.shape == (3,)
    assert model.sigma.shape == (3, 3)


def test_continuous_pomdp_prediction_and_belief_update():
    model = ContinuousPOMDPActiveInference(
        state_dim=2,
        obs_dim=2,
        action_dim=2,
        dt=0.1,
        prior_mean=np.array([1.0, 2.0]),
    )
    obs = np.array([1.2, 2.1])
    action = np.array([0.1, -0.1])

    mu_post, sigma_post, vfe = model.update_beliefs(obs, action)

    assert mu_post.shape == (2,)
    assert sigma_post.shape == (2, 2)
    assert np.isfinite(vfe)
    assert len(model.history) == 1
    assert model.history[0]["free_energy"] == vfe


def test_continuous_pomdp_action_selection_towards_target():
    # Target state is positive in state dimension
    model = ContinuousPOMDPActiveInference(
        state_dim=2,
        obs_dim=2,
        action_dim=2,
        target_prior=np.array([5.0, 5.0]),
        prior_mean=np.array([0.0, 0.0]),
    )
    action = model.select_action(horizon=5)
    # Action selected should be positive to approach the target of [5.0, 5.0]
    assert np.all(action > 0)
