"""Tests for climate projections module."""

import numpy as np
import pandas as pd
import pytest
import xarray as xr

from geo_infer_climate.core.projections import ClimateProjections


@pytest.fixture
def projector():
    return ClimateProjections()


def _historical_linear(slope_per_year: float, start_year: int = 2000, n_years: int = 11) -> xr.DataArray:
    """Linear series starting at 10 deg C with an exact per-year slope."""
    years = np.arange(start_year, start_year + n_years)
    values = 10.0 + slope_per_year * (years - start_year)
    return xr.DataArray(
        values,
        dims=["time"],
        coords={"time": pd.date_range(f"{start_year}-01-01", periods=n_years, freq="YS")},
    )


class TestProjectFutureClimate:
    def test_known_trend_extrapolates_correctly(self, projector):
        # Exact linear series with 0.1 deg C/yr trend; ssp245 factor is 1.0.
        # The projection anchors on the historical mean (10.5, the 2005
        # value) plus trend * years_ahead (2050 - 2010 = 40):
        # 10.5 + 0.1 * 40 = 14.5.
        hist = _historical_linear(0.1)
        projected = projector.project_future_climate(hist, scenario="ssp245", years=[2050])
        assert float(projected.values[0]) == pytest.approx(14.5, abs=1e-6)

    def test_scenario_scaling_is_monotonic(self, projector):
        hist = _historical_linear(0.1)
        values = {}
        for scenario in ["ssp126", "ssp245", "ssp370", "ssp585"]:
            projected = projector.project_future_climate(hist, scenario=scenario, years=[2100])
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
        projected = projector.project_future_climate(hist, scenario="ssp245", years=[2050])
        assert float(projected.values[0]) == pytest.approx(14.5, abs=1e-6)
