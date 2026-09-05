"""Tests for water infrastructure planning module."""

import numpy as np
import pytest
import xarray as xr

from geo_infer_water.core.water_infrastructure import WaterInfrastructurePlanner


@pytest.fixture
def planner():
    return WaterInfrastructurePlanner()


class TestOptimizeWaterAllocation:
    def test_sufficient_supply_meets_all_demand(self, planner):
        # When supply exceeds total demand every demander is fully met.
        demand = xr.DataArray([40.0, 30.0, 30.0], dims=["user"])
        supply = xr.DataArray(120.0)
        result = planner.optimize_water_allocation(supply, demand)
        np.testing.assert_allclose(result["allocation"].values, demand.values)
        assert float(result["shortage"].sum()) == 0.0

    def test_proportional_allocation_without_priorities(self, planner):
        # Equal priorities (default): scarce supply is split by demand share.
        demand = xr.DataArray([50.0, 30.0, 20.0], dims=["user"])
        supply = xr.DataArray(50.0)
        result = planner.optimize_water_allocation(supply, demand)
        # Total allocated cannot exceed supply.
        assert float(result["allocation"].sum()) <= 50.0 + 1e-9
        # Larger demanders receive a larger share.
        assert float(result["allocation"].values[0]) > float(result["allocation"].values[2])

    def test_priority_weighting_favours_high_priority_demand(self, planner):
        # Equal demands, different priorities: the higher-priority demander
        # receives a larger allocation under scarcity.
        demand = xr.DataArray([50.0, 50.0], dims=["user"])
        priorities = xr.DataArray([1.0, 9.0], dims=["user"])
        supply = xr.DataArray(50.0)
        result = planner.optimize_water_allocation(supply, demand, priorities=priorities)
        assert float(result["allocation"].values[1]) > float(result["allocation"].values[0])

    def test_allocation_never_exceeds_demand(self, planner):
        demand = xr.DataArray([10.0, 90.0], dims=["user"])
        priorities = xr.DataArray([9.0, 1.0], dims=["user"])
        supply = xr.DataArray(100.0)
        result = planner.optimize_water_allocation(supply, demand, priorities=priorities)
        assert float(result["allocation"].values[0]) <= 10.0 + 1e-9
        assert float(result["allocation"].values[1]) <= 90.0 + 1e-9

    def test_shortage_is_unmet_demand(self, planner):
        demand = xr.DataArray([60.0, 60.0], dims=["user"])
        supply = xr.DataArray(60.0)
        result = planner.optimize_water_allocation(supply, demand)
        np.testing.assert_allclose(
            result["shortage"].values,
            np.maximum(demand.values - result["allocation"].values, 0.0),
            atol=1e-9,
        )

    def test_result_variables_present(self, planner):
        demand = xr.DataArray([40.0, 30.0], dims=["user"])
        supply = xr.DataArray(70.0)
        result = planner.optimize_water_allocation(supply, demand)
        for var in ("allocation", "shortage", "supply_demand_ratio", "adequacy"):
            assert var in result


class TestAssessInfrastructureNeeds:
    def test_capacity_gap_when_demand_exceeds_capacity(self, planner):
        capacity = xr.DataArray([100.0, 200.0], dims=["site"])
        demand = xr.DataArray([150.0, 180.0], dims=["site"])
        result = planner.assess_infrastructure_needs(capacity, demand)
        np.testing.assert_allclose(result["capacity_gap"].values, [50.0, 0.0])
        assert bool(result["expansion_needed"].values[0]) is True
        assert bool(result["expansion_needed"].values[1]) is False

    def test_adequacy_ratio(self, planner):
        capacity = xr.DataArray([100.0], dims=["site"])
        demand = xr.DataArray([200.0], dims=["site"])
        result = planner.assess_infrastructure_needs(capacity, demand)
        assert float(result["adequacy"].values[0]) == pytest.approx(0.5)
