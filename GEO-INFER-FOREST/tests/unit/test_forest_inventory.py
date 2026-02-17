"""
Unit tests for forest inventory.
"""

import numpy as np
import pytest
import xarray as xr

from geo_infer_forest.core.forest_inventory import ForestInventory


class TestForestInventory:
    """Test suite for ForestInventory."""
    
    def test_initialization(self):
        """Test inventory initialization."""
        inventory = ForestInventory()
        assert inventory is not None
    
    def test_estimate_biomass(self):
        """Test biomass estimation."""
        inventory = ForestInventory()
        forest_cover = xr.DataArray(
            np.array([[80.0, 60.0], [40.0, 90.0]]),
            dims=("y", "x"),
        )
        result = inventory.estimate_biomass(forest_cover)
        assert result is not None
        assert float(result.max()) > 0


