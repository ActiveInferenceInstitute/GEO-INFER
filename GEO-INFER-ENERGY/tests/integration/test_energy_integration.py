"""
Integration tests for GEO-INFER-ENERGY: renewable resource assessment and demand forecasting pipeline.

Tests RenewableResourceAssessor and EnergyDemandForecaster working together in an
energy planning pipeline using synthetic xarray data.
"""

import pytest
import numpy as np

try:
    import xarray as xr
    HAS_XARRAY = True
except ImportError:
    HAS_XARRAY = False

pytestmark = [
    pytest.mark.integration,
]


@pytest.fixture
def solar_irradiance():
    """Create synthetic solar irradiance data (kWh/m2/day)."""
    np.random.seed(42)
    return xr.DataArray(
        np.random.uniform(4.0, 7.0, (10, 10)),
        dims=["lat", "lon"],
        coords={
            "lat": np.linspace(33.0, 35.0, 10),
            "lon": np.linspace(-119.0, -117.0, 10),
        },
    )


@pytest.fixture
def wind_speed():
    """Create synthetic wind speed data (m/s)."""
    np.random.seed(43)
    return xr.DataArray(
        np.random.uniform(4.0, 12.0, (10, 10)),
        dims=["lat", "lon"],
        coords={
            "lat": np.linspace(33.0, 35.0, 10),
            "lon": np.linspace(-119.0, -117.0, 10),
        },
    )


@pytest.fixture
def hourly_generation():
    """Create synthetic hourly generation profile (MW) for 24 hours."""
    np.random.seed(44)
    hours = np.arange(24)
    # Solar-like profile: peaks at noon
    solar_profile = np.maximum(0, np.sin(np.pi * (hours - 6) / 12)) * 100
    noise = np.random.uniform(-5, 5, 24)
    return xr.DataArray(
        np.maximum(0, solar_profile + noise),
        dims=["time"],
        coords={"time": hours},
    )


@pytest.fixture
def hourly_demand():
    """Create synthetic hourly demand profile (MW) for 24 hours."""
    np.random.seed(45)
    hours = np.arange(24)
    # Demand: bimodal peaks at morning and evening
    demand = 50 + 30 * np.sin(np.pi * hours / 12) + 20 * np.sin(np.pi * (hours - 6) / 6)
    noise = np.random.uniform(-3, 3, 24)
    return xr.DataArray(
        np.maximum(20, demand + noise),
        dims=["time"],
        coords={"time": hours},
    )


class TestSolarAssessmentPipeline:
    """Test solar energy assessment from irradiance data through LCOE calculation."""

    def test_solar_potential_assessment(self, solar_irradiance):
        """Test solar potential assessment produces valid output."""
        from geo_infer_energy.core.renewable_resources import RenewableResourceAssessor

        assessor = RenewableResourceAssessor()
        result = assessor.assess_solar_potential(solar_irradiance)

        assert "solar_potential" in result
        assert "annual_energy" in result
        assert float(result["solar_potential"].min()) > 0, "Solar potential should be positive"
        assert result["annual_energy"].shape == solar_irradiance.shape

    def test_solar_with_terrain(self, solar_irradiance):
        """Test solar assessment with slope and aspect terrain data."""
        from geo_infer_energy.core.renewable_resources import RenewableResourceAssessor

        slope = xr.DataArray(
            np.random.uniform(0, 45, solar_irradiance.shape),
            dims=solar_irradiance.dims,
            coords=solar_irradiance.coords,
        )
        aspect = xr.DataArray(
            np.random.uniform(0, 360, solar_irradiance.shape),
            dims=solar_irradiance.dims,
            coords=solar_irradiance.coords,
        )

        assessor = RenewableResourceAssessor()
        result = assessor.assess_solar_potential(solar_irradiance, slope=slope, aspect=aspect)

        assert float(result["solar_potential"].min()) >= 0
        # Terrain correction should reduce some values compared to no-terrain
        result_no_terrain = assessor.assess_solar_potential(solar_irradiance)
        assert float(result["solar_potential"].mean()) <= float(result_no_terrain["solar_potential"].mean())


class TestWindAssessmentPipeline:
    """Test wind energy assessment pipeline."""

    def test_wind_potential_assessment(self, wind_speed):
        """Test wind potential from speed data."""
        from geo_infer_energy.core.renewable_resources import RenewableResourceAssessor

        assessor = RenewableResourceAssessor()
        result = assessor.assess_wind_potential(wind_speed)

        assert "wind_power" in result
        assert "energy_potential" in result
        # Wind power is proportional to v^3
        assert float(result["wind_power"].min()) > 0

    def test_wind_capacity_factor(self, wind_speed):
        """Test capacity factor calculation for a wind turbine."""
        from geo_infer_energy.core.renewable_resources import (
            RenewableResourceAssessor, RenewableType,
        )

        assessor = RenewableResourceAssessor()
        # Flatten to 1D time series
        wind_ts = xr.DataArray(
            wind_speed.values.flatten()[:100],
            dims=["time"],
        )

        cf_result = assessor.calculate_capacity_factor(
            RenewableType.ONSHORE_WIND, wind_ts, rated_capacity_mw=2.0,
        )

        assert 0 <= cf_result["capacity_factor"] <= 1
        assert cf_result["rated_capacity_mw"] == 2.0
        assert cf_result["annual_generation_mwh"] > 0
        assert cf_result["hours_analyzed"] == 100


class TestSiteSuitabilityPipeline:
    """Test site suitability assessment."""

    def test_site_suitability_scoring(self):
        """Test suitability scoring with constraints."""
        from geo_infer_energy.core.renewable_resources import (
            RenewableResourceAssessor, RenewableType,
        )

        assessor = RenewableResourceAssessor()

        # Excellent solar site
        result = assessor.assess_site_suitability(
            location=(-118.0, 34.0),
            resource_type=RenewableType.SOLAR_PV,
            resource_value=6.5,
        )
        assert result["suitability_class"] == "excellent"
        assert result["development_recommended"] is True

        # Protected area constraint should make it unsuitable
        result_constrained = assessor.assess_site_suitability(
            location=(-118.0, 34.0),
            resource_type=RenewableType.SOLAR_PV,
            resource_value=6.5,
            constraints={"protected_area": True},
        )
        assert result_constrained["suitability_class"] == "unsuitable"
        assert result_constrained["development_recommended"] is False

    def test_lcoe_calculation(self):
        """Test LCOE calculation for a solar project."""
        from geo_infer_energy.core.renewable_resources import (
            RenewableResourceAssessor, RenewableType,
        )

        assessor = RenewableResourceAssessor()
        lcoe = assessor.calculate_lcoe(
            resource_type=RenewableType.SOLAR_PV,
            capacity_mw=10.0,
            capacity_factor=0.22,
        )

        assert lcoe["lcoe_usd_kwh"] > 0
        assert lcoe["lcoe_usd_mwh"] > 0
        assert lcoe["annual_generation_mwh"] > 0
        assert lcoe["lifetime_generation_gwh"] > 0
        assert lcoe["competitiveness"] in ["Competitive", "Moderately competitive", "High cost"]


class TestPortfolioAndStoragePipeline:
    """Test portfolio management and storage requirement analysis."""

    def test_register_sites_and_get_portfolio(self):
        """Test registering renewable sites and getting portfolio summary."""
        from geo_infer_energy.core.renewable_resources import (
            RenewableResourceAssessor, RenewableType, RenewableSite,
        )

        assessor = RenewableResourceAssessor()

        sites = [
            RenewableSite("s1", "Desert Solar", (-115.0, 35.0), RenewableType.SOLAR_PV, 50.0, 0.25, 109.5),
            RenewableSite("s2", "Mountain Wind", (-117.0, 34.5), RenewableType.ONSHORE_WIND, 30.0, 0.35, 91.98),
            RenewableSite("s3", "Coast Solar", (-118.5, 33.8), RenewableType.SOLAR_PV, 20.0, 0.20, 35.04),
        ]

        for site in sites:
            assessor.register_site(site)

        summary = assessor.get_portfolio_summary()
        assert summary["site_count"] == 3
        assert summary["total_capacity_mw"] == 100.0
        assert "solar_pv" in summary["by_resource_type"]
        assert "onshore_wind" in summary["by_resource_type"]
        assert summary["by_resource_type"]["solar_pv"]["count"] == 2

    def test_storage_requirements_analysis(self, hourly_generation, hourly_demand):
        """Test storage requirement analysis for renewable integration."""
        from geo_infer_energy.core.renewable_resources import RenewableResourceAssessor

        assessor = RenewableResourceAssessor()
        result = assessor.analyze_storage_requirements(
            hourly_generation, hourly_demand, renewable_penetration=0.5,
        )

        assert "renewable_penetration" in result
        assert result["renewable_penetration"] == 0.5
        assert result["total_demand_mwh"] > 0
        assert "recommended_storage" in result
        assert result["recommended_storage"]["duration_hours"] == 4.0
        assert result["curtailment_rate_pct"] >= 0


class TestDemandForecastingPipeline:
    """Test energy demand forecasting."""

    def test_demand_forecast_basic(self):
        """Test basic demand forecasting from historical data."""
        from geo_infer_energy.core.energy_demand import EnergyDemandForecaster

        forecaster = EnergyDemandForecaster()

        # Create historical demand data with upward trend
        historical = xr.DataArray(
            np.array([100, 105, 110, 115, 120, 125, 130], dtype=float),
            dims=["time"],
            coords={"time": np.arange(7)},
        )

        result = forecaster.forecast_demand(historical, forecast_years=5)
        assert "demand_forecast" in result
        # Forecast should continue the trend
        forecast_vals = result["demand_forecast"].values.flatten()
        assert len(forecast_vals) == 5

    def test_peak_demand_identification(self):
        """Test peak demand identification from time series."""
        from geo_infer_energy.core.energy_demand import EnergyDemandForecaster

        forecaster = EnergyDemandForecaster()

        demand = xr.DataArray(
            np.array([50, 60, 80, 100, 90, 70, 55], dtype=float),
            dims=["time"],
            coords={"time": np.arange(7)},
        )

        result = forecaster.identify_peak_demand(demand)
        assert "peak_demand" in result
        assert "average_demand" in result
        assert "peak_factor" in result
        assert float(result["peak_demand"]) == 100.0
        assert float(result["peak_factor"]) > 1.0
