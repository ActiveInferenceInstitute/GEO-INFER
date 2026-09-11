"""Tests for climate projections module."""

import numpy as np
import pandas as pd
import pytest
import xarray as xr

from geo_infer_climate.core.projections import ClimateProjections


@pytest.fixture
def projector():
    return ClimateProjections()


def _historical_linear(
    slope_per_year: float, start_year: int = 2000, n_years: int = 11
) -> xr.DataArray:
    """Linear series starting at 10 deg C with an exact per-year slope."""
    years = np.arange(start_year, start_year + n_years)
    values = 10.0 + slope_per_year * (years - start_year)
    return xr.DataArray(
        values,
        dims=["time"],
        coords={
            "time": pd.date_range(f"{start_year}-01-01", periods=n_years, freq="YS")
        },
    )


class TestProjectFutureClimate:
    def test_known_trend_extrapolates_correctly(self, projector):
        # Exact linear series with 0.1 deg C/yr trend; ssp245 factor is 1.0.
        # The least-squares line passes through the historical mean (10.5,
        # the mid-2005 value on a calendar-year axis), so the 2050 projection
        # is 10.5 + 0.1 * (2050 - 2005) = 15.0 (tiny leap-day fuzz for
        # datetime coordinates).
        hist = _historical_linear(0.1)
        projected = projector.project_future_climate(
            hist, scenario="ssp245", years=[2050]
        )
        assert float(projected.values[0]) == pytest.approx(15.0, abs=1e-2)

    def test_scenario_scaling_is_monotonic(self, projector):
        hist = _historical_linear(0.1)
        values = {}
        for scenario in ["ssp126", "ssp245", "ssp370", "ssp585"]:
            projected = projector.project_future_climate(
                hist, scenario=scenario, years=[2100]
            )
            values[scenario] = float(projected.values[0])
        assert values["ssp126"] < values["ssp245"] < values["ssp370"] < values["ssp585"]

    def test_unknown_scenario_raises(self, projector):
        hist = _historical_linear(0.1)
        with pytest.raises(ValueError):
            projector.project_future_climate(hist, scenario="rcp85")

    def test_default_years_present(self, projector):
        hist = _historical_linear(0.1)
        projected = projector.project_future_climate(hist)
        assert projected.sizes["time"] == 2
        assert [int(t) for t in projected.time.dt.year.values] == [2050, 2100]

    def test_numeric_year_time_coordinate(self, projector):
        # A float year index on the time coordinate must also work.
        hist = _historical_linear(0.1)
        hist = hist.assign_coords(time=np.arange(2000.0, 2011.0))
        projected = projector.project_future_climate(
            hist, scenario="ssp245", years=[2050]
        )
        assert float(projected.values[0]) == pytest.approx(15.0, abs=1e-6)

    def test_monthly_and_annual_same_span_identical_projections(self, projector):
        # GS-150: the trend slope is per calendar year, so monthly and
        # annual series covering the same span (both exactly linear in
        # elapsed 365.25-day years) must yield the same projection. Under
        # the old per-index-step slope the monthly projection was ~12x low.
        slope = 0.1
        annual_dates = pd.date_range("2000-01-01", periods=11, freq="YS")
        annual_days = (annual_dates - annual_dates[0]).days.values.astype(float)
        annual = xr.DataArray(
            10.0 + slope * annual_days / 365.25,
            dims=["time"],
            coords={"time": annual_dates},
        )
        monthly_dates = pd.date_range("2000-01-01", "2010-12-01", freq="MS")
        monthly_days = (monthly_dates - monthly_dates[0]).days.values.astype(float)
        monthly = xr.DataArray(
            10.0 + slope * monthly_days / 365.25,
            dims=["time"],
            coords={"time": monthly_dates},
        )
        from_annual = projector.project_future_climate(annual, years=[2050])
        from_monthly = projector.project_future_climate(monthly, years=[2050])
        assert float(from_monthly.values[0]) == pytest.approx(
            float(from_annual.values[0]), rel=1e-9
        )
        assert float(from_annual.values[0]) == pytest.approx(15.0, abs=1e-6)

    def test_monthly_trend_is_per_year_not_per_step(self, projector):
        # A monthly series rising 0.1 deg C per *year* must extrapolate at
        # the per-year rate, not be deflated by the per-step slope.
        dates = pd.date_range("2000-01-01", periods=120, freq="MS")
        years_elapsed = (dates.year - 2000) + (dates.month - 1) / 12.0
        hist = xr.DataArray(
            10.0 + 0.1 * years_elapsed, dims=["time"], coords={"time": dates}
        )
        projected = projector.project_future_climate(
            hist, scenario="ssp245", years=[2050]
        )
        # mean (10.49 at mid-2004.96) + 0.1 * (2050 - 2004.96)
        assert float(projected.values[0]) == pytest.approx(15.0, abs=1e-2)
