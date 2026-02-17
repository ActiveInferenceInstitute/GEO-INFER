"""Unit tests for renewable resource assessment."""

import numpy as np
import pytest
import xarray as xr

from geo_infer_energy.core.renewable_resources import RenewableResourceAssessor


class TestRenewableResourceAssessor:
    """Test suite for RenewableResourceAssessor."""

    def test_initialization(self):
        """Test assessor initialization."""
        assessor = RenewableResourceAssessor()
        assert assessor is not None

    def test_solar_potential_assessment(self):
        """Test solar potential assessment."""
        assessor = RenewableResourceAssessor()
        irradiance = xr.DataArray(
            np.full((3, 3), 5.0), dims=("y", "x")
        )
        result = assessor.assess_solar_potential(irradiance)
        assert "solar_potential" in result
        assert "annual_energy" in result
        assert float(result["solar_potential"].min()) > 0

    def test_wind_potential_assessment(self):
        """Test wind potential assessment."""
        assessor = RenewableResourceAssessor()
        wind = xr.DataArray(
            np.full((3, 3), 8.0), dims=("y", "x")
        )
        result = assessor.assess_wind_potential(wind)
        assert "wind_power" in result
        assert "energy_potential" in result
        assert float(result["wind_power"].min()) > 0
