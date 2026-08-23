"""Contract tests for the improved AEP curve and extreme-value PML estimation.

The AEP curve is checked for monotonicity, determinism and clamping.  The
extreme-value PML is fit to a heavy-tailed synthetic book and checked to rise
past the observed record -- which a purely empirical PML could never do.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from geo_infer_risk.utils.risk_metrics import (
    calculate_aep_curve,
    calculate_pml,
    estimate_pml_with_tail_fit,
    _fit_exceedance_tail,
)


@pytest.fixture
def heavy_tail_losses() -> np.ndarray:
    """800 heavy-tailed per-event losses over a plausible long record."""
    rng = np.random.default_rng(2026)
    return rng.lognormal(mean=6.0, sigma=1.6, size=800)


@pytest.fixture
def ramp() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "event_id": [f"e{i}" for i in range(20)],
            "hazard_type": ["eq"] * 20,
            "loss": [50.0 * (i + 1) for i in range(20)],
        }
    )


class TestAepCurve:
    def test_curve_is_non_increasing_in_threshold(self, ramp: pd.DataFrame) -> None:
        curve = calculate_aep_curve(
            ramp,
            thresholds=[0.0, 250.0, 500.0, 750.0, 1000.0, 1_000_000.0],
            num_years=4000,
            random_seed=5,
            exposure_years=10.0,
        )
        assert curve["aep"] == sorted(curve["aep"], reverse=True)
        assert curve["aep"][-1] == 0.0

    def test_deterministic_with_a_fixed_seed(self, ramp: pd.DataFrame) -> None:
        kwargs = {
            "thresholds": [100.0, 200.0, 300.0, 500.0],
            "num_years": 2000,
            "exposure_years": 10.0,
            "random_seed": 11,
        }
        assert calculate_aep_curve(ramp, **kwargs) == calculate_aep_curve(ramp, **kwargs)

    def test_low_threshold_is_almost_certain_for_a_dense_year(
        self, ramp: pd.DataFrame
    ) -> None:
        curve = calculate_aep_curve(
            ramp, thresholds=[0.0], num_years=5000, random_seed=1, exposure_years=1.0
        )
        assert curve["aep"][0] > 0.99

    def test_empty_table_returns_zero_aep(self) -> None:
        empty = pd.DataFrame({"event_id": [], "hazard_type": [], "loss": []})
        curve = calculate_aep_curve(empty, thresholds=[1.0, 2.0])
        assert curve["aep"] == [0.0, 0.0]

    def test_rejects_a_non_finite_threshold(self, ramp: pd.DataFrame) -> None:
        with pytest.raises(ValueError, match="threshold"):
            calculate_aep_curve(ramp, thresholds=[float("nan")])


class TestPmlTailFit:
    def test_extreme_tail_rises_past_the_observed_record(
        self, heavy_tail_losses: np.ndarray
    ) -> None:
        empirical_max = float(np.max(heavy_tail_losses))
        result = estimate_pml_with_tail_fit(
            heavy_tail_losses,
            return_period=5000,
            exposure_years=100.0,
            threshold_percentile=0.7,
        )
        assert result["method"] == "gpd_tail"
        assert result["pml"] > empirical_max

    def test_matches_empirical_pml_when_tail_is_fit(
        self, heavy_tail_losses: np.ndarray
    ) -> None:
        # The empirical PML clamps at the record maximum, the fitted value
        # continues past it, so the fitted PML is strictly larger for a very
        # long return period.
        empirical = calculate_pml(heavy_tail_losses, return_period=10000)
        fitted = estimate_pml_with_tail_fit(
            heavy_tail_losses,
            return_period=10000,
            exposure_years=100.0,
            threshold_percentile=0.7,
        )["pml"]
        assert fitted > empirical

    def test_pml_increases_with_return_period(
        self, heavy_tail_losses: np.ndarray
    ) -> None:
        values = [
            estimate_pml_with_tail_fit(
                heavy_tail_losses,
                return_period=rp,
                exposure_years=100.0,
            )["pml"]
            for rp in (250, 1000, 5000, 20000)
        ]
        assert values == sorted(values)

    def test_tail_slope_is_negative(self, heavy_tail_losses: np.ndarray) -> None:
        slope, _, _, _ = _fit_exceedance_tail(heavy_tail_losses, 100.0, 0.7)
        assert slope < 0.0

    def test_empty_book_is_zero(self) -> None:
        result = estimate_pml_with_tail_fit(
            np.array([]), return_period=100, exposure_years=1.0
        )
        assert result["pml"] == 0.0

    def test_rejects_a_bad_return_period(self, heavy_tail_losses: np.ndarray) -> None:
        with pytest.raises(ValueError, match="return_period"):
            estimate_pml_with_tail_fit(heavy_tail_losses, return_period=1.0)

    def test_rejects_an_invalid_tail_percentile(
        self, heavy_tail_losses: np.ndarray
    ) -> None:
        with pytest.raises(ValueError, match="threshold_percentile"):
            estimate_pml_with_tail_fit(
                heavy_tail_losses,
                return_period=100,
                exposure_years=10.0,
                threshold_percentile=1.0,
            )

    def test_rejects_a_short_record(self) -> None:
        # Three events cannot support a three-point tail fit.
        with pytest.raises(ValueError, match="tail"):
            estimate_pml_with_tail_fit(
                np.array([1.0, 2.0, 3.0]),
                return_period=100,
                exposure_years=1.0,
            )