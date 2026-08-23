"""
Unit tests for discrete-categorical expected free energy computation on the
generative model (core.generative_model.GenerativeModel).

These pin the behavioural contract: scalar vs decomposed EFE agreement,
policy selection favouring the policy whose predicted belief matches the
preference prior, and rejection of non-categorical model types.
"""

from __future__ import annotations

from typing import cast

import numpy as np
import pytest

from geo_infer_act import FreeEnergyBreakdown
from geo_infer_act.core.generative_model import GenerativeModel


def _categorical_model(seed: int = 1) -> GenerativeModel:
    return GenerativeModel(
        "categorical",
        {
            "state_dim": 4,
            "obs_dim": 4,
            "prior_precision": 1.0,
            "random_seed": seed,
        },
    )


def _policies() -> list[dict]:
    return [
        {"action": "matches", "predicted_beliefs": [0.8, 0.1, 0.1, 0.1]},
        {"action": "mismatches", "predicted_beliefs": [0.1, 0.1, 0.1, 0.7]},
    ]


def test_efe_returns_decomposition_and_ordered_scores() -> None:
    """EFE recognises which policy aligns with preferences."""
    model = _categorical_model()
    preferences = np.array([0.8, 0.1, 0.1, 0.1])
    result = cast(
        dict,
        model.compute_expected_free_energy(
            _policies(), preferences, return_breakdowns=True
        ),
    )
    efe = np.asarray(result["efe_scores"], dtype=float)
    assert result["best_index"] == 0
    assert efe[0] < efe[1]
    np.testing.assert_allclose(result["posterior"].sum(), 1.0, atol=1e-6)
    assert len(result["epistemic_values"]) == 2
    assert all(np.isfinite(value) for value in result["pragmatic_values"])


def test_efe_scalar_best_matches_decomposed() -> None:
    """Scalar best-EFE equals the argmin of the decomposed score list."""
    model = _categorical_model()
    preferences = np.array([0.8, 0.1, 0.1, 0.1])
    result = cast(
        dict,
        model.compute_expected_free_energy(
            _policies(), preferences, return_breakdowns=True
        ),
    )
    best_scalar = model.compute_expected_free_energy(_policies(), preferences)
    assert best_scalar == pytest.approx(min(result["efe_scores"]), rel=1e-9)


def test_efe_breakdown_objects_are_typed() -> None:
    """The decomposed collection is derived from typed breakdowns."""
    model = _categorical_model()
    result = cast(dict, model.compute_expected_free_energy(_policies(), return_breakdowns=True))
    # The public API returns numeric lists; re-run one policy through the
    # calculator to confirm the underlying objects remain typed.
    breakdown = model.free_energy_calculator.compute_expected_free_energy(
        model._categorical_belief_vector(), _policies()[0],
        model._categorical_preference_vector(4), return_breakdown=True,
    )
    assert isinstance(breakdown, FreeEnergyBreakdown)


def test_gaussian_model_rejects_efe() -> None:
    """Continuous (Gaussian) generative models must reject discrete EFE."""
    model = GenerativeModel("gaussian", {"state_dim": 2, "obs_dim": 2})
    with pytest.raises(ValueError, match="categorical"):
        model.compute_expected_free_energy([{"action": 0}])