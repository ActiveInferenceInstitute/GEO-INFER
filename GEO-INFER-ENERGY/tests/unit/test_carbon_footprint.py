"""Tests for carbon footprint analysis module."""

import numpy as np
import pytest
import xarray as xr

import sys
sys.path.insert(0, "GEO-INFER-ENERGY/src")

from geo_infer_energy.core.carbon_footprint import CarbonFootprintAnalyzer


@pytest.fixture
def analyzer():
    return CarbonFootprintAnalyzer()


class TestEmissions:
    def test_coal_highest_emissions(self, analyzer):
        energy = xr.DataArray(np.full((3, 3), 1000.0), dims=("y", "x"))
        coal_em = analyzer.calculate_emissions(energy, "coal")
        gas_em = analyzer.calculate_emissions(energy, "natural_gas")
        assert float(coal_em.mean()) > float(gas_em.mean())

    def test_solar_zero_emissions(self, analyzer):
        energy = xr.DataArray(np.full((3, 3), 1000.0), dims=("y", "x"))
        solar_em = analyzer.calculate_emissions(energy, "solar")
        np.testing.assert_allclose(solar_em.values, 0.0)

    def test_emission_proportional_to_energy(self, analyzer):
        e1 = xr.DataArray(np.full((3, 3), 100.0), dims=("y", "x"))
        e2 = xr.DataArray(np.full((3, 3), 200.0), dims=("y", "x"))
        em1 = analyzer.calculate_emissions(e1, "natural_gas")
        em2 = analyzer.calculate_emissions(e2, "natural_gas")
        ratio = float(em2.mean() / em1.mean())
        assert abs(ratio - 2.0) < 0.01


class TestCarbonIntensity:
    def test_intensity_calculation(self, analyzer):
        emissions = xr.DataArray(np.full((3, 3), 500.0), dims=("y", "x"))
        energy = xr.DataArray(np.full((3, 3), 1000.0), dims=("y", "x"))
        intensity = analyzer.calculate_carbon_intensity(emissions, energy)
        np.testing.assert_allclose(intensity.values, 0.5)


class TestRenewableImpact:
    def test_emissions_reduction(self, analyzer):
        renewable = xr.DataArray(np.full((3, 3), 500.0), dims=("y", "x"))
        total = xr.DataArray(np.full((3, 3), 1000.0), dims=("y", "x"))
        baseline = xr.DataArray(np.full((3, 3), 500000.0), dims=("y", "x"))
        result = analyzer.assess_renewable_impact(renewable, total, baseline)
        assert float(result["emissions_avoided"].mean()) > 0
        assert float(result["renewable_fraction"].mean()) == pytest.approx(0.5, abs=0.01)
