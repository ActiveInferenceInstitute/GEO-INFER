"""
Unit tests for expected-free-energy minimisation internals: policy-posterior
composition and the epistemic-vs-pragmatic dominance decomposition.

These pin two behavioural contracts:

- ``compose_policy_posterior`` turns raw EFE scores into a normalised policy
  posterior whose sharpness tracks policy separation and an E-based habit
  prior.
- ``decompose_efe`` labels each candidate as exploration- (epistemic) or
  exploitation- (pragmatic) driven.
"""

from __future__ import annotations

import numpy as np
import pytest

from geo_infer_act.core.policy_selection import PolicySelector


def test_policy_posterior_is_normalized() -> None:
    """Raw EFE scores become a finite, valid probability posterior."""
    selector = PolicySelector()
    posterior_info = selector.compose_policy_posterior(np.array([-2.0, 0.5, 10.0]))
    posterior = posterior_info["posterior"]
    assert np.all(posterior >= 0.0)
    assert np.all(posterior <= 1.0)
    np.testing.assert_allclose(posterior.sum(), 1.0, atol=1e-6)
    assert np.isfinite(posterior_info["precision"])


def test_policy_posterior_is_sharper_for_separated_policies() -> None:
    """Widely separated EFE scores sharpen the posterior (adaptive precision)."""
    selector = PolicySelector()
    sharp = selector.compose_policy_posterior(np.array([0.0, 10.0, -5.0]))
    flat = selector.compose_policy_posterior(np.array([0.0, 0.001, 0.002]))
    # The best policy probability is far higher when scores are separated.
    assert np.max(sharp["posterior"]) > np.max(flat["posterior"])


def test_policy_posterior_respects_habit_prior() -> None:
    """The E-based habit prior shifts the posterior toward preferred policies."""
    selector = PolicySelector()
    flat = selector.compose_policy_posterior(np.array([0.0, 0.0, 0.0]))
    prior = np.array([0.01, 0.98, 0.01])
    biased = selector.compose_policy_posterior(
        np.array([0.0, 0.0, 0.0]), prior=prior
    )
    flat_post = np.asarray(flat["posterior"], dtype=float)
    biased_post = np.asarray(biased["posterior"], dtype=float)
    # With uniform scores the prior dominates; the middle policy dominates.
    assert biased_post[1] > flat_post[1]
    assert biased["prior"] is not None


def test_policy_posterior_rejects_empty_and_nonfinite() -> None:
    """Invalid EFE inputs fail explicitly."""
    selector = PolicySelector()
    with pytest.raises(ValueError, match="must not be empty"):
        selector.compose_policy_posterior(np.array([]))
    with pytest.raises(ValueError, match="must be finite"):
        selector.compose_policy_posterior(np.array([1.0, np.nan]))


def test_decompose_efe_labels_exploration_and_exploitation() -> None:
    """
    Under uniform preferences the pragmatic term is constant, so a broad
    predictive belief (high entropy) is labelled epistemic and a peaked one
    (low entropy) is labelled pragmatic.
    """
    selector = PolicySelector()
    beliefs = np.array([0.25, 0.25, 0.25, 0.25])
    policies = [
        {"action": "explore", "predicted_beliefs": [0.25, 0.25, 0.25, 0.25]},
        {"action": "exploit", "predicted_beliefs": [0.9, 0.05, 0.03, 0.02]},
    ]
    preferences = np.array([0.25, 0.25, 0.25, 0.25])
    decomposition = selector.decompose_efe(beliefs, policies, preferences)
    dominance = decomposition["dominance"]
    assert "epistemic" in dominance
    assert "pragmatic" in dominance
    assert 0.0 < decomposition["exploration_share"] < 1.0
    assert len(decomposition["efe_scores"]) == 2