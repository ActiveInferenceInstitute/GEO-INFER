"""Unit tests for renewable resource assessment (merged from root-level suite)."""

import numpy as np
import pytest
import xarray as xr

from geo_infer_energy import RenewableResourceAssessor, RenewableType, SuitabilityClass, RenewableSite


@pytest.fixture
def assessor():
    return RenewableResourceAssessor()


class TestRenewableResourceAssessor:
    """Resource-potential assessments."""

    def test_init(self, assessor):
        assert RenewableType.ONSHORE_WIND in assessor.capital_costs

    def test_assess_solar_potential(self, assessor):
        irradiance = xr.DataArray(np.full((3, 3), 5.0), dims=("y", "x"))
        result = assessor.assess_solar_potential(irradiance)
        assert "solar_potential" in result
        assert "annual_energy" in result
        # 5.0 kWh/m2/day * 365 days, 20% efficiency
        assert float(result["solar_potential"].mean()) == pytest.approx(5.0 * 365)
        assert float(result["annual_energy"].mean()) == pytest.approx(5.0 * 365 * 0.2)

    def test_assess_solar_with_terrain(self, assessor):
        slope = xr.DataArray(np.array([[30.0, 10.0]]), dims=("y", "x"))
        result = assessor.assess_solar_potential(xr.DataArray(np.full((1, 2), 5.0), dims=("y", "x")), slope=slope)
        # Optimal 30-degree slope scores higher than 10 degrees
        assert float(result["solar_potential"].values[0, 0]) > float(result["solar_potential"].values[0, 1])

    def test_assess_wind_potential(self, assessor):
        wind = xr.DataArray(np.full((3, 3), 8.0), dims=("y", "x"))
        result = assessor.assess_wind_potential(wind)
        assert "wind_power" in result
        assert "energy_potential" in result
        assert float(result["wind_power"].mean()) == pytest.approx(8.0 ** 3)

    def test_assess_hydro_potential(self, assessor):
        flow = xr.DataArray(np.array([[1.0, 3.0]]), dims=("y", "x"))
        head = xr.DataArray(np.array([[100.0, 100.0]]), dims=("y", "x"))
        result = assessor.assess_hydro_potential(flow, head)
        # P = rho * g * Q * h * eta / 1e6 MW
        expected = 1000 * 9.81 * 1.0 * 100.0 * 0.85 / 1e6
        assert float(result["hydro_power"].values[0, 0]) == pytest.approx(expected)
        assert float(result["hydro_power"].values[0, 1]) > float(result["hydro_power"].values[0, 0])


class TestSiteSuitability:
    """Site suitability scoring."""

    def test_assess_excellent_site(self, assessor):
        result = assessor.assess_site_suitability(
            location=(-118.25, 34.05), resource_type=RenewableType.SOLAR_PV, resource_value=7.0
        )
        assert result["suitability_class"] == "excellent"
        assert result["development_recommended"] is True
        assert result["final_score"] == pytest.approx(1.0)

    def test_assess_poor_site(self, assessor):
        result = assessor.assess_site_suitability(
            location=(-118.25, 34.05), resource_type=RenewableType.SOLAR_PV, resource_value=2.0
        )
        assert result["suitability_class"] in ("marginal", "unsuitable")

    def test_constraints_affect_suitability(self, assessor):
        without_constraints = assessor.assess_site_suitability(
            location=(-118.0, 34.0), resource_type=RenewableType.ONSHORE_WIND, resource_value=8.0
        )
        with_constraints = assessor.assess_site_suitability(
            location=(-118.0, 34.0),
            resource_type=RenewableType.ONSHORE_WIND,
            resource_value=8.0,
            constraints={"poor_access": True, "steep_slope": True},
        )
        assert with_constraints["final_score"] < without_constraints["final_score"]
        # 0.8 (poor access) * 0.7 (steep slope) penalties
        assert with_constraints["final_score"] == pytest.approx(0.8 * 0.7)

    def test_protected_area_blocks_development(self, assessor):
        result = assessor.assess_site_suitability(
            location=(-118.0, 34.0),
            resource_type=RenewableType.SOLAR_PV,
            resource_value=7.0,
            constraints={"protected_area": True},
        )
        assert result["development_recommended"] is False
        assert result["final_score"] == 0


class TestCapacityFactor:
    """Capacity factor calculation."""

    def test_solar_capacity_factor(self, assessor):
        hours = np.arange(8760)
        irradiance = np.maximum(0, 500 * np.sin(2 * np.pi * (hours % 24) / 24 - np.pi / 4))
        result = assessor.calculate_capacity_factor(
            RenewableType.SOLAR_PV, xr.DataArray(irradiance, dims=["time"]), rated_capacity_mw=100
        )
        assert 0 < result["capacity_factor"] < 0.5
        assert result["annual_generation_mwh"] == pytest.approx(result["capacity_factor"] * 100 * 8760)

    def test_wind_capacity_factor(self, assessor):
        rng = np.random.default_rng(42)
        wind_speeds = rng.weibull(2, 8760) * 8
        result = assessor.calculate_capacity_factor(
            RenewableType.ONSHORE_WIND, xr.DataArray(wind_speeds, dims=["time"]), rated_capacity_mw=50
        )
        assert 0 < result["capacity_factor"] < 1.0
        assert result["hours_zero_output"] > 0  # speeds below cut-in (3 m/s)

    def test_zero_series_default_branch_is_guarded(self, assessor):
        """Regression: all-zero resource series must give CF 0, not NaN."""
        zeros = xr.DataArray(np.zeros(24), dims=["time"])
        result = assessor.calculate_capacity_factor(RenewableType.GEOTHERMAL, zeros)
        assert result["capacity_factor"] == 0.0
        assert result["annual_generation_mwh"] == 0.0


class TestLCOE:
    """LCOE calculation."""

    def test_calculate_lcoe_solar(self, assessor):
        result = assessor.calculate_lcoe(
            resource_type=RenewableType.SOLAR_PV, capacity_mw=100, capacity_factor=0.25
        )
        assert result["lcoe_usd_mwh"] > 0
        # Solar PV: $1000/kW capital, 2% O&M, 25 y, 7% discount
        assert 20 < result["lcoe_usd_mwh"] < 80

    def test_lcoe_varies_with_capacity_factor(self, assessor):
        low_cf = assessor.calculate_lcoe(RenewableType.ONSHORE_WIND, capacity_mw=50, capacity_factor=0.25)
        high_cf = assessor.calculate_lcoe(RenewableType.ONSHORE_WIND, capacity_mw=50, capacity_factor=0.40)
        assert high_cf["lcoe_usd_mwh"] < low_cf["lcoe_usd_mwh"]

    def test_lcoe_factors(self, assessor):
        result = assessor.calculate_lcoe(
            RenewableType.SOLAR_PV, capacity_mw=100, capacity_factor=0.25,
            discount_rate=0.08, lifetime_years=30,
        )
        assert result["lifetime_years"] == 30
        assert result["discount_rate"] == 0.08


class TestStorageAnalysis:
    """Storage requirement analysis."""

    def test_analyze_storage_requirements(self, assessor):
        hours = np.arange(168)
        generation = np.maximum(0, 500 * np.sin(2 * np.pi * (hours % 24) / 24 - np.pi / 4))
        demand = 400 + 200 * np.sin(2 * np.pi * (hours % 24) / 24)
        result = assessor.analyze_storage_requirements(
            xr.DataArray(generation, dims=["time"]), xr.DataArray(demand, dims=["time"]),
            renewable_penetration=0.5,
        )
        assert result["recommended_storage"]["duration_hours"] == 4.0
        assert result["recommended_storage"]["energy_capacity_mwh"] == pytest.approx(
            result["recommended_storage"]["power_capacity_mw"] * 4.0
        )

    def test_storage_duration_is_configurable(self, assessor):
        hours = np.arange(168)
        generation = np.maximum(0, 500 * np.sin(2 * np.pi * (hours % 24) / 24 - np.pi / 4))
        demand = 400 + 200 * np.sin(2 * np.pi * (hours % 24) / 24)
        gen = xr.DataArray(generation, dims=["time"])
        dem = xr.DataArray(demand, dims=["time"])
        result = assessor.analyze_storage_requirements(gen, dem, duration_hours=8.0)
        assert result["recommended_storage"]["duration_hours"] == 8.0
        assert result["recommended_storage"]["energy_capacity_mwh"] == pytest.approx(
            result["recommended_storage"]["power_capacity_mw"] * 8.0
        )

    def test_deficit_measured_against_full_demand(self, assessor):
        """Regression: deficit must be vs full demand, not penetration-scaled demand."""
        gen = xr.DataArray(np.full(24, 50.0), dims=["time"])
        dem = xr.DataArray(np.full(24, 100.0), dims=["time"])
        result = assessor.analyze_storage_requirements(gen, dem, renewable_penetration=0.5)
        # scaled generation == 50 MW/h exactly; deficit per hour = 100 - 50 = 50
        assert result["max_hourly_deficit_mw"] == pytest.approx(50.0)
        assert result["recommended_storage"]["power_capacity_mw"] == pytest.approx(50.0)


class TestSiteRegistry:
    """Site registry and portfolio summary."""

    def test_register_site(self, assessor):
        site = RenewableSite(
            site_id="SOLAR_001", name="Desert Solar Farm", location=(-115.5, 33.0),
            resource_type=RenewableType.SOLAR_PV, capacity_mw=100, capacity_factor=0.28,
            annual_generation_gwh=245.3,
        )
        assert assessor.register_site(site) == "SOLAR_001"
        assert "SOLAR_001" in assessor.site_registry

    def test_portfolio_summary(self, assessor):
        sites = [
            RenewableSite("S1", "Solar 1", (-115, 33), RenewableType.SOLAR_PV, 100, 0.25, 219),
            RenewableSite("S2", "Solar 2", (-116, 34), RenewableType.SOLAR_PV, 150, 0.27, 355),
            RenewableSite("W1", "Wind 1", (-117, 35), RenewableType.ONSHORE_WIND, 200, 0.35, 613),
        ]
        for site in sites:
            assessor.register_site(site)
        summary = assessor.get_portfolio_summary()
        assert summary["site_count"] == 3
        assert summary["total_capacity_mw"] == 450
        assert summary["total_generation_gwh"] == pytest.approx(219 + 355 + 613)
        assert summary["by_resource_type"]["solar_pv"]["capacity_mw"] == 250

    def test_empty_portfolio(self, assessor):
        assert assessor.get_portfolio_summary() == {"error": "No sites registered"}


class TestEnums:
    """Public data model."""

    def test_renewable_types_values(self):
        assert RenewableType.SOLAR_PV.value == "solar_pv"
        assert RenewableType.HYDROPOWER.value == "hydropower"

    def test_suitability_classes(self):
        assert [c.value for c in SuitabilityClass] == [
            "excellent", "good", "moderate", "marginal", "unsuitable"
        ]
