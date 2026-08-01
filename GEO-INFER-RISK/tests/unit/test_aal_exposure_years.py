"""Regression tests for calculate_aal exposure-years semantics (STATS-04).

AAL must be annualized by the number of exposure years the loss table
spans, not by the number of distinct events (which over-estimates AAL
whenever multiple events occur per year).
"""

import logging

import pandas as pd
import pytest

from geo_infer_risk.utils.risk_metrics import calculate_aal


@pytest.fixture
def multi_event_table():
    """4 events across 2 exposure years."""
    return pd.DataFrame(
        {
            "event_id": ["e1", "e2", "e3", "e4"],
            "hazard_type": ["flood"] * 4,
            "loss": [100.0, 100.0, 100.0, 100.0],
        }
    )


def test_aal_with_exposure_years_annualizes_correctly(multi_event_table):
    """AAL = total loss / exposure years (400 / 2 = 200)."""
    result = calculate_aal(multi_event_table, exposure_years=2.0)
    assert result["total"] == pytest.approx(200.0)
    assert result["by_hazard"]["flood"] == pytest.approx(200.0)


def test_aal_exposure_years_positive_required(multi_event_table):
    """Zero or negative exposure years is rejected."""
    with pytest.raises(ValueError, match="exposure_years"):
        calculate_aal(multi_event_table, exposure_years=0)
    with pytest.raises(ValueError, match="exposure_years"):
        calculate_aal(multi_event_table, exposure_years=-1)


def test_aal_legacy_event_count_semantics_warns(multi_event_table, caplog):
    """Legacy path (no exposure_years) warns and uses event-count semantics."""
    with caplog.at_level(logging.WARNING, logger="geo_infer_risk"):
        result = calculate_aal(multi_event_table)
    assert result["total"] == pytest.approx(100.0)  # 400 / 4 events
    assert any("exposure_years" in rec.message for rec in caplog.records)


def test_aal_exposure_years_matches_legacy_when_one_event_per_year():
    """When each event spans one year, both semantics agree."""
    table = pd.DataFrame(
        {
            "event_id": ["e1", "e2"],
            "hazard_type": ["wind", "wind"],
            "loss": [50.0, 150.0],
        }
    )
    legacy = calculate_aal(table)
    annual = calculate_aal(table, exposure_years=2.0)
    assert legacy["total"] == pytest.approx(annual["total"])