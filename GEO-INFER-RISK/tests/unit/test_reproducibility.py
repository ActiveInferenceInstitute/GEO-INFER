"""Tests for explicit random-seed threading in RISK.

Two properties are checked for every stochastic entry point:

* Replay -- equal seeds give equal output, distinct seeds give distinct output.
* Isolation -- the process-wide ``numpy.random`` stream is never read or
  advanced, so a caller's global state cannot silently change a risk number and
  a risk run cannot perturb a caller's own stream.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from geo_infer_risk.core.catastrophe_models import (
    CatastropheConfig,
    EnhancedEarthquakeModel,
)
from geo_infer_risk.utils.risk_metrics import (
    calculate_annual_aggregate_exceedance_probability,
)


@pytest.fixture
def loss_table() -> pd.DataFrame:
    """A three-event loss table."""
    return pd.DataFrame(
        {
            "event_id": ["e1", "e2", "e3"],
            "hazard_type": ["eq", "eq", "eq"],
            "loss": [10.0, 5.0, 8.0],
        }
    )


def _make_earthquake_model() -> EnhancedEarthquakeModel:
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
    """simulate_events with a seed replays identically."""
    a = _make_earthquake_model().simulate_events(5, random_seed=7)
    b = _make_earthquake_model().simulate_events(5, random_seed=7)
    assert len(a) == len(b) == 5
    assert [e["event_id"] for e in a] == [e["event_id"] for e in b]


def test_earthquake_simulate_events_different_seeds_differ() -> None:
    a = _make_earthquake_model().simulate_events(5, random_seed=1)
    b = _make_earthquake_model().simulate_events(5, random_seed=2)
    assert [e["event_id"] for e in a] != [e["event_id"] for e in b]


def test_earthquake_simulate_events_accepts_a_generator() -> None:
    """A caller-owned Generator is threaded through instead of a seed."""
    a = _make_earthquake_model().simulate_events(
        4, random_seed=np.random.default_rng(21)
    )
    b = _make_earthquake_model().simulate_events(
        4, random_seed=np.random.default_rng(21)
    )
    assert [e["event_id"] for e in a] == [e["event_id"] for e in b]


def test_earthquake_simulate_events_leaves_global_stream_untouched() -> None:
    """Simulation neither reads nor advances the numpy.random singleton."""
    np.random.seed(5)
    expected = np.random.random()

    np.random.seed(5)
    _make_earthquake_model().simulate_events(5)
    assert np.random.random() == expected


def test_aep_seed_replay(loss_table: pd.DataFrame) -> None:
    a = calculate_annual_aggregate_exceedance_probability(
        loss_table, threshold=20.0, num_years=500, random_seed=9, exposure_years=3.0
    )
    b = calculate_annual_aggregate_exceedance_probability(
        loss_table, threshold=20.0, num_years=500, random_seed=9, exposure_years=3.0
    )
    assert a == b
    assert 0.0 <= a <= 1.0


def test_aep_different_seeds_differ(loss_table: pd.DataFrame) -> None:
    """Distinct seeds give distinct Monte Carlo estimates."""
    a = calculate_annual_aggregate_exceedance_probability(
        loss_table, threshold=15.0, num_years=2000, random_seed=1, exposure_years=3.0
    )
    b = calculate_annual_aggregate_exceedance_probability(
        loss_table, threshold=15.0, num_years=2000, random_seed=2, exposure_years=3.0
    )
    assert a != b


def test_aep_accepts_a_generator(loss_table: pd.DataFrame) -> None:
    a = calculate_annual_aggregate_exceedance_probability(
        loss_table,
        threshold=20.0,
        num_years=500,
        random_seed=np.random.default_rng(4),
        exposure_years=3.0,
    )
    b = calculate_annual_aggregate_exceedance_probability(
        loss_table,
        threshold=20.0,
        num_years=500,
        random_seed=np.random.default_rng(4),
        exposure_years=3.0,
    )
    assert a == b


def test_aep_leaves_global_stream_untouched(loss_table: pd.DataFrame) -> None:
    """The AEP Monte Carlo draws from its own generator, not the singleton."""
    np.random.seed(5)
    expected = np.random.random()

    np.random.seed(5)
    calculate_annual_aggregate_exceedance_probability(
        loss_table, threshold=20.0, num_years=300, exposure_years=3.0
    )
    assert np.random.random() == expected
