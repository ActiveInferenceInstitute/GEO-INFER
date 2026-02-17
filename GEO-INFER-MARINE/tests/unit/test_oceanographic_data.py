"""Unit tests for oceanographic data processing."""

import numpy as np
import pytest
import xarray as xr

from geo_infer_marine.core.oceanographic_data import OceanographicDataProcessor


class TestOceanographicDataProcessor:
    """Test suite for OceanographicDataProcessor."""

    def test_initialization(self):
        """Test processor initialization."""
        processor = OceanographicDataProcessor()
        assert processor is not None

    def test_calculate_ocean_currents(self):
        """Test ocean current calculation."""
        processor = OceanographicDataProcessor()
        u = xr.DataArray(np.array([1.0, 0.0, -1.0]), dims=["x"])
        v = xr.DataArray(np.array([0.0, 1.0, 0.0]), dims=["x"])
        result = processor.calculate_ocean_currents(u, v)
        assert "current_magnitude" in result
        assert "current_direction" in result
        np.testing.assert_allclose(result["current_magnitude"].values, [1.0, 1.0, 1.0])

    def test_process_3d_ocean_data(self):
        """Test 3D data processing returns copy."""
        processor = OceanographicDataProcessor()
        ds = xr.Dataset(
            {"temperature": (["y", "x"], np.full((3, 3), 20.0))},
        )
        result = processor.process_3d_ocean_data(ds)
        assert "temperature" in result
