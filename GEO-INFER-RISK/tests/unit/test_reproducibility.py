"""Tests for deterministic random-seed threading in RISK.

Verifies the REPRO-01 migration: the catastrophe simulation and the annual
aggregate exceedance probability (AEP) Monte Carlo accept ``random_seed`` and
produce identical output across calls for the same seed, while the default
continues to use the legacy global ``np.random`` state.
"""

from __future__ import annotations

import pandas as pd

from geo_infer_risk.core.catastrophe_models import (
    CatastropheConfig,
    EnhancedEarthquakeModel,
)
from geo_infer_risk.utils.risk_metrics import (
    calculate_annual_aggregate_exceedance_probability,
)


def _make_earthquake_model():
    config = CatastropheConfig(
        simulation_years=10,
        return_periods=[10, 25, 50],
        simulation_method="monte_carlo",
        spatial_correlation=False,
        batch_size=10,
    )
    model = EnhancedEarthquakeModel(config=config)
    # Provide minimal model parameters so hazard generation runs.
    model.model_parameters = {"mean_depth": 15.0}
    return model


def test_earthquake_simulate_events_seed_replay() -> None:
    a = _make_earthquake_model().simulate_events(5, random_seed=7)
    b = _make_earthquake_model().simulate_events(5, random_seed=7)
    # Same seed => same count and, for EQ events, same ids.
    assert len(a) == len(b) == 5
    assert [e["event_id"] for e in a] == [e["event_id"] for e in b]


def test_earthquake_simulate_events_different_seeds_differ() -> None:
    a = _make_earthquake_model().simulate_events(5, random_seed=1)
    b = _make_earthquake_model().simulate_events(5, random_seed=2)
    assert [e["event_id"] for e in a] != [e["event_id"] for e in b]


def test_aep_seed_replay() -> None:
    df = pd.DataFrame(
        {"event_id": ["e1", "e2", "e3"], "hazard_type": ["eq", "eq", "eq"], "loss": [10.0, 5.0, 8.0]}
    )
    a = calculate_annual_aggregate_exceedance_probability(
        df, threshold=20.0, num_years=500, random_seed=9
    )
    b = calculate_annual_aggregate_exceedance_probability(
        df, threshold=20.0, num_years=500, random_seed=9
    )
    assert a == b
    assert 0.0 <= a <= 1.0


def test_aep_default_uses_global_state() -> None:
    df = pd.DataFrame(
        {"event_id": ["e1", "e2", "e3"], "hazard_type": ["eq", "eq", "eq"], "loss": [10.0, 5.0, 8.0]}
    )
    import numpy as np

    np.random.seed(5)
    a = calculate_annual_aggregate_exceedance_probability(df, threshold=20.0, num_years=300)
    np.random.seed(5)
    b = calculate_annual_aggregate_exceedance_probability(df, threshold=20.0, num_years=300)
    assert a == b
