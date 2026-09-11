"""Tests for sea-level rise analysis module."""

import numpy as np
import pytest
import xarray as xr

from geo_infer_marine.core.sea_level import SeaLevelAnalyzer


@pytest.fixture
def analyzer():
    return SeaLevelAnalyzer()


@pytest.fixture
def historical_sea_level():
    """Rising sea-level record: 10 mm/yr over 2000-2010."""
    years = np.arange(2000, 2011)
    values = (years - 2000) * 10.0
    return xr.DataArray(
        values,
        dims="time",
        coords={
            "time": np.array([f"{y}-01-01" for y in years], dtype="datetime64[ns]")
        },
    )


class TestProjectSeaLevelRise:
    def test_higher_scenario_projects_higher(self, analyzer, historical_sea_level):
        rcp45 = analyzer.project_sea_level_rise(historical_sea_level, scenario="rcp45")
        rcp85 = analyzer.project_sea_level_rise(historical_sea_level, scenario="rcp85")
        rcp45_2100 = float(rcp45.sel(time="2100-01-01"))
        rcp85_2100 = float(rcp85.sel(time="2100-01-01"))
        assert rcp85_2100 > rcp45_2100

    def test_projection_extends_time_coordinate(self, analyzer, historical_sea_level):
        result = analyzer.project_sea_level_rise(
            historical_sea_level, scenario="rcp45", years=[2050, 2100]
        )

        assert {str(t)[:4] for t in result.time.values} == {"2050", "2100"}
        result = analyzer.project_sea_level_rise(historical_sea_level, scenario="rcp85")
        mean_historical = float(historical_sea_level.mean())
        assert float(result.max()) > mean_historical

    def test_unknown_scenario_falls_back_to_rcp45(self, analyzer, historical_sea_level):
        default = analyzer.project_sea_level_rise(
            historical_sea_level, scenario="rcp45"
        )
        unknown = analyzer.project_sea_level_rise(
            historical_sea_level, scenario="bogus"
        )
        assert float(unknown.max()) == float(default.max())

    def test_projection_absolute_values_match_linear_model(
        self, analyzer, historical_sea_level
    ):
        """GS-166: projections equal mean + per-year trend * years_ahead."""
        result = analyzer.project_sea_level_rise(
            historical_sea_level, scenario="rcp45", years=[2050, 2100]
        )
        mean_historical = float(historical_sea_level.mean())
        # Fixture: 10 mm/yr over 2000-2010, last year 2010.
        assert float(result.sel(time="2050-01-01")) == pytest.approx(
            mean_historical + 10.0 * (2050 - 2010)
        )
        assert float(result.sel(time="2100-01-01")) == pytest.approx(
            mean_historical + 10.0 * (2100 - 2010)
        )

    def test_scenario_factor_scales_trend(self, analyzer, historical_sea_level):
        rcp45 = analyzer.project_sea_level_rise(
            historical_sea_level, scenario="rcp45", years=[2050]
        )
        rcp85 = analyzer.project_sea_level_rise(
            historical_sea_level, scenario="rcp85", years=[2050]
        )
        mean_historical = float(historical_sea_level.mean())
        expected_rcp45 = mean_historical + 10.0 * (2050 - 2010)
        assert float(rcp85.sel(time="2050-01-01")) == pytest.approx(
            mean_historical + 2.0 * 10.0 * (2050 - 2010)
        )
        assert float(rcp45.sel(time="2050-01-01")) == pytest.approx(expected_rcp45)

    def test_multidimensional_historical_data_raises_value_error(
        self, analyzer, historical_sea_level
    ):
        """GS-166: (space, time) input gets a clear error, not a TypeError."""
        two_d = xr.DataArray(
            np.tile(historical_sea_level.values, (2, 1)),
            dims=("space", "time"),
            coords={"time": historical_sea_level.time.values, "space": [0, 1]},
        )
        with pytest.raises(ValueError, match="one-dimensional"):
            analyzer.project_sea_level_rise(two_d, scenario="rcp45", years=[2050])


class TestAssessInundation:
    def test_low_elevation_inundated(self, analyzer):
        elevation = xr.DataArray([1.0, 5.0, 10.0], dims="cell")
        sea_level = xr.DataArray(3.0)
        result = analyzer.assess_inundation(elevation, sea_level)
        inundated = result["inundated"].values
        assert bool(inundated[0]) is True
        assert bool(inundated[1]) is False
        assert bool(inundated[2]) is False

    def test_inundation_depth_positive_only_where_inundated(self, analyzer):
        elevation = xr.DataArray([1.0, 5.0], dims="cell")
        sea_level = xr.DataArray(3.0)
        result = analyzer.assess_inundation(elevation, sea_level)
        depth = result["inundation_depth"].values
        assert float(depth[0]) == pytest.approx(2.0)
        assert float(depth[1]) == pytest.approx(0.0)
