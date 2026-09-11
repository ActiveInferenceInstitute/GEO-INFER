"""Tests for energy grid optimization module."""

import numpy as np
import pytest
import xarray as xr

import sys

sys.path.insert(0, "GEO-INFER-ENERGY/src")

from geo_infer_energy.core.energy_grid import EnergyGridOptimizer


@pytest.fixture
def optimizer():
    return EnergyGridOptimizer()


class TestGridOptimization:
    def test_balanced_grid(self, optimizer):
        demand = xr.DataArray(np.full((5, 5), 100.0), dims=("y", "x"))
        supply = xr.DataArray(np.full((5, 5), 100.0), dims=("y", "x"))
        result = optimizer.optimize_grid_network(demand, supply)
        np.testing.assert_allclose(result["balance"].values, 0.0)
        np.testing.assert_allclose(result["reliability"].values, 1.0)

    def test_deficit_detection(self, optimizer):
        demand = xr.DataArray(np.full((5, 5), 150.0), dims=("y", "x"))
        supply = xr.DataArray(np.full((5, 5), 100.0), dims=("y", "x"))
        result = optimizer.optimize_grid_network(demand, supply)
        assert float(result["deficit"].sum()) > 0

    def test_surplus_detection(self, optimizer):
        demand = xr.DataArray(np.full((5, 5), 50.0), dims=("y", "x"))
        supply = xr.DataArray(np.full((5, 5), 100.0), dims=("y", "x"))
        result = optimizer.optimize_grid_network(demand, supply)
        assert float(result["surplus"].sum()) > 0

    def test_transmission_capacity_clips_surplus(self, optimizer):
        """transmission_capacity clips surplus/deficit instead of being ignored (GS-176)."""
        demand = xr.DataArray(np.full((5, 5), 50.0), dims=("y", "x"))
        supply = xr.DataArray(np.full((5, 5), 100.0), dims=("y", "x"))
        capacity = xr.DataArray(np.full((5, 5), 10.0), dims=("y", "x"))

        unconstrained = optimizer.optimize_grid_network(demand, supply)
        constrained = optimizer.optimize_grid_network(
            demand, supply, transmission_capacity=capacity
        )

        # Pre-fix: results identical with/without the parameter (dead).
        assert float(constrained["surplus"].max()) < float(
            unconstrained["surplus"].max()
        )
        np.testing.assert_allclose(constrained["surplus"].values, 10.0)

    def test_transmission_capacity_clips_deficit(self, optimizer):
        demand = xr.DataArray(np.full((5, 5), 150.0), dims=("y", "x"))
        supply = xr.DataArray(np.full((5, 5), 100.0), dims=("y", "x"))
        capacity = xr.DataArray(np.full((5, 5), 10.0), dims=("y", "x"))

        result = optimizer.optimize_grid_network(
            demand, supply, transmission_capacity=capacity
        )
        np.testing.assert_allclose(result["deficit"].values, 10.0)


class TestGridReliability:
    def test_adequate_capacity(self, optimizer):
        capacity = xr.DataArray(np.full((3, 3), 200.0), dims=("y", "x"))
        demand = xr.DataArray(np.full((3, 3), 100.0), dims=("y", "x"))
        result = optimizer.assess_grid_reliability(capacity, demand)
        np.testing.assert_allclose(result["reliability_index"].values, 1.0)

    def test_inadequate_capacity(self, optimizer):
        capacity = xr.DataArray(np.full((3, 3), 80.0), dims=("y", "x"))
        demand = xr.DataArray(np.full((3, 3), 100.0), dims=("y", "x"))
        result = optimizer.assess_grid_reliability(capacity, demand)
        assert float(result["reliability_index"].mean()) < 1.0
        assert float(result["capacity_deficit"].sum()) > 0
