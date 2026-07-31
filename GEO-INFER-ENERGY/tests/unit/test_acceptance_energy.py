"""
DOMAIN-01 Acceptance tests for GEO-INFER-ENERGY documented features.

These tests exercise real implemented behavior for documented features that
previously lacked focused acceptance tests:

1. EnergyInfrastructurePlanner.optimize_facility_siting — facility siting
   optimization combining resource potential and demand proximity.
2. EnergyInfrastructurePlanner.assess_infrastructure_capacity — capacity
   gap analysis and annual growth projection.

No mocks, stubs, or placeholders: every assertion exercises actual code paths.
"""

import numpy as np
import pytest
import xarray as xr

from geo_infer_energy.core.energy_infrastructure import EnergyInfrastructurePlanner


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def planner() -> EnergyInfrastructurePlanner:
    return EnergyInfrastructurePlanner()


@pytest.fixture
def resource_potential() -> xr.DataArray:
    """A 5×5 grid of resource potential values (0–100)."""
    lat = np.linspace(40, 41, 5)
    lon = np.linspace(-74, -73, 5)
    data = np.array([
        [10, 20, 30, 40, 50],
        [20, 40, 60, 80, 90],
        [30, 60, 90, 80, 70],
        [20, 40, 60, 50, 40],
        [10, 20, 30, 20, 10],
    ], dtype=float)
    return xr.DataArray(data, dims=["lat", "lon"], coords={"lat": lat, "lon": lon})


@pytest.fixture
def demand_centers() -> xr.DataArray:
    """A 5×5 grid of demand center density values."""
    lat = np.linspace(40, 41, 5)
    lon = np.linspace(-74, -73, 5)
    data = np.array([
        [5, 10, 15, 10, 5],
        [10, 20, 30, 20, 10],
        [15, 30, 50, 30, 15],
        [10, 20, 30, 20, 10],
        [5, 10, 15, 10, 5],
    ], dtype=float)
    return xr.DataArray(data, dims=["lat", "lon"], coords={"lat": lat, "lon": lon})


@pytest.fixture
def constraints() -> xr.DataArray:
    """A 5×5 constraint mask (1=allowed, 0=excluded)."""
    lat = np.linspace(40, 41, 5)
    lon = np.linspace(-74, -73, 5)
    data = np.ones((5, 5))
    data[0, 0] = 0  # Exclude top-left corner
    data[4, 4] = 0  # Exclude bottom-right corner
    return xr.DataArray(data, dims=["lat", "lon"], coords={"lat": lat, "lon": lon})


# ---------------------------------------------------------------------------
# optimize_facility_siting
# ---------------------------------------------------------------------------

class TestOptimizeFacilitySiting:
    """Acceptance: facility siting optimization produces valid results."""

    def test_returns_dataset_with_required_vars(self, planner, resource_potential, demand_centers):
        """The result Dataset contains all documented output variables."""
        result = planner.optimize_facility_siting(resource_potential, demand_centers)
        assert "suitability" in result.data_vars
        assert "optimal_sites" in result.data_vars
        assert "resource_suitability" in result.data_vars
        assert "demand_proximity" in result.data_vars

    def test_suitability_is_normalized(self, planner, resource_potential, demand_centers):
        """Suitability values are in [0, 1] after normalization."""
        result = planner.optimize_facility_siting(resource_potential, demand_centers)
        suit = result.suitability.values
        assert suit.min() >= 0.0
        assert suit.max() <= 1.0 + 1e-9

    def test_resource_suitability_normalized(self, planner, resource_potential, demand_centers):
        """Resource suitability is normalized by max."""
        result = planner.optimize_facility_siting(resource_potential, demand_centers)
        rs = result.resource_suitability.values
        assert abs(rs.max() - 1.0) < 1e-9  # Max becomes 1.0

    def test_optimal_sites_are_boolean(self, planner, resource_potential, demand_centers):
        """Optimal sites mask is boolean."""
        result = planner.optimize_facility_siting(resource_potential, demand_centers)
        assert result.optimal_sites.dtype == bool

    def test_optimal_sites_are_top_10_percent(self, planner, resource_potential, demand_centers):
        """Optimal sites are the top 10th percentile of suitability."""
        result = planner.optimize_facility_siting(resource_potential, demand_centers)
        suit = result.suitability.values
        optimal = result.optimal_sites.values
        threshold = np.quantile(suit, 0.9)
        # All optimal sites should have suitability >= threshold
        assert np.all(suit[optimal] >= threshold - 1e-9)

    def test_constraints_exclude_areas(self, planner, resource_potential, demand_centers, constraints):
        """Constraints mask zeroes out excluded areas in suitability."""
        result = planner.optimize_facility_siting(resource_potential, demand_centers, constraints=constraints)
        suit = result.suitability.values
        # Excluded cells should have zero suitability
        assert suit[0, 0] == 0.0
        assert suit[4, 4] == 0.0
        # Allowed cells should be positive
        assert suit[2, 2] > 0.0

    def test_shape_preserved(self, planner, resource_potential, demand_centers):
        """Output shapes match input shapes."""
        result = planner.optimize_facility_siting(resource_potential, demand_centers)
        assert result.suitability.shape == resource_potential.shape


# ---------------------------------------------------------------------------
# assess_infrastructure_capacity
# ---------------------------------------------------------------------------

class TestAssessInfrastructureCapacity:
    """Acceptance: capacity assessment computes gaps and growth needs."""

    @pytest.fixture
    def current_capacity(self) -> xr.DataArray:
        lat = np.linspace(40, 41, 3)
        lon = np.linspace(-74, -73, 3)
        return xr.DataArray(
            np.full((3, 3), 100.0), dims=["lat", "lon"],
            coords={"lat": lat, "lon": lon}
        )

    @pytest.fixture
    def projected_demand(self) -> xr.DataArray:
        lat = np.linspace(40, 41, 3)
        lon = np.linspace(-74, -73, 3)
        return xr.DataArray(
            np.full((3, 3), 150.0), dims=["lat", "lon"],
            coords={"lat": lat, "lon": lon}
        )

    def test_returns_dataset_with_required_vars(
        self, planner, current_capacity, projected_demand
    ):
        """Result contains all documented output variables."""
        result = planner.assess_infrastructure_capacity(current_capacity, projected_demand)
        assert "current_capacity" in result.data_vars
        assert "required_capacity" in result.data_vars
        assert "capacity_gap" in result.data_vars
        assert "annual_growth_needed" in result.data_vars

    def test_capacity_gap_positive_when_demand_exceeds_capacity(
        self, planner, current_capacity, projected_demand
    ):
        """Gap is positive when projected demand > current capacity."""
        result = planner.assess_infrastructure_capacity(current_capacity, projected_demand)
        gap = result.capacity_gap.values
        assert np.all(gap == 50.0)

    def test_annual_growth_computed(
        self, planner, current_capacity, projected_demand
    ):
        """Annual growth = (demand - capacity) / years."""
        result = planner.assess_infrastructure_capacity(
            current_capacity, projected_demand, years=10
        )
        growth = result.annual_growth_needed.values
        assert np.allclose(growth, 5.0)  # (150-100)/10 = 5

    def test_required_capacity_equals_demand(
        self, planner, current_capacity, projected_demand
    ):
        """Required capacity equals projected demand."""
        result = planner.assess_infrastructure_capacity(current_capacity, projected_demand)
        assert np.allclose(result.required_capacity.values, projected_demand.values)

    def test_zero_gap_when_balanced(self, planner):
        """Gap is zero when capacity equals demand."""
        lat = np.linspace(40, 41, 2)
        lon = np.linspace(-74, -73, 2)
        cap = xr.DataArray(np.full((2, 2), 100.0), dims=["lat", "lon"],
                           coords={"lat": lat, "lon": lon})
        dem = xr.DataArray(np.full((2, 2), 100.0), dims=["lat", "lon"],
                           coords={"lat": lat, "lon": lon})
        result = planner.assess_infrastructure_capacity(cap, dem)
        assert np.allclose(result.capacity_gap.values, 0.0)

    def test_negative_gap_when_surplus(self, planner):
        """Gap is negative when capacity exceeds demand (surplus)."""
        lat = np.linspace(40, 41, 2)
        lon = np.linspace(-74, -73, 2)
        cap = xr.DataArray(np.full((2, 2), 200.0), dims=["lat", "lon"],
                           coords={"lat": lat, "lon": lon})
        dem = xr.DataArray(np.full((2, 2), 100.0), dims=["lat", "lon"],
                           coords={"lat": lat, "lon": lon})
        result = planner.assess_infrastructure_capacity(cap, dem)
        assert np.all(result.capacity_gap.values < 0)
